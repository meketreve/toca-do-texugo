#!/usr/bin/env python3
"""Acesso de fora do PC (acesso.py) e as rotas que ele protege no server.py.

Duas partes:
- unidade: filtro de IP, Host, cookie e as regras do codigo (validade, uso unico, limite de erros,
  trava global) com relogio falso -- sem esperar 2 min de verdade;
- ponta a ponta: sobe o server.py com HOME temporario e `pareamento_local: false` (senao o
  loopback entra direto e nao ha o que testar) e faz o caminho do tablet por HTTP.

    python3 testes/teste-acesso.py

Precisa do psutil (o server.py importa). Nada da maquina e lido: o HOME e uma pasta temporaria.
"""
import http.client
import json
import os
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
import acesso  # noqa: E402


class Relogio:
    def __init__(self):
        self.t = 1_000_000.0

    def __call__(self):
        return self.t


class Filtros(unittest.TestCase):
    def test_cliente(self):
        for ip in ("127.0.0.1", "::1", "192.168.0.20", "10.1.2.3", "172.20.0.5", "100.101.102.103",
                   "fd7a:115c:a1e0::1", "::ffff:192.168.0.20"):
            self.assertTrue(acesso.cliente_ok(ip), ip)
        for ip in ("8.8.8.8", "100.128.0.1", "2001:4860::1", "0.0.0.0", "224.0.0.1", "lixo", ""):
            self.assertFalse(acesso.cliente_ok(ip), ip)

    def test_host(self):
        ok = ("127.0.0.1:8787", "localhost:8787", "192.168.0.20:8787", "[::1]:8787", "LOCALHOST:8787",
              "pc.tail1234.ts.net:8787")
        for h in ok:
            self.assertTrue(acesso.host_ok(h, 8787, ["pc.tail1234.ts.net"]), h)
        for h in ("evil.com:8787", "127.0.0.1:80", "127.0.0.1", "192.168.0.20.nip.io:8787", "", "[::1]", "[::1]x"):
            self.assertFalse(acesso.host_ok(h, 8787, ["pc.tail1234.ts.net"]), h)

    def test_cookie(self):
        self.assertEqual(acesso.cookie_token("a=1; toca=abc; b=2"), "abc")
        self.assertIsNone(acesso.cookie_token("tocax=abc"))
        self.assertIsNone(acesso.cookie_token(None))
        c = acesso.set_cookie("xyz")
        for parte in ("toca=xyz", "HttpOnly", "SameSite=Strict", "Path=/"):
            self.assertIn(parte, c)


class Codigo(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.rel = Relogio()
        self.avisos = []
        self.disp = acesso.Dispositivos(Path(self.tmp.name) / "d.json", relogio=self.rel)
        self.par = acesso.Pareamento(self.disp, self.avisos.append, relogio=self.rel)

    def tearDown(self):
        self.tmp.cleanup()

    def codigo(self):
        return self.par.estado(local=True)["codigo"]

    def errado(self):
        c = self.codigo()
        return f"{(int(c) + 1) % 10 ** 6:06d}"

    def test_caminho_feliz_e_uso_unico(self):
        self.assertTrue(self.par.pedir()["ok"])
        c = self.codigo()
        self.assertRegex(c, r"^\d{6}$")
        self.assertEqual(self.avisos, [c])
        tok = self.par.tentar(c, "tablet")["token"]
        self.assertGreaterEqual(len(tok), 43)
        self.assertTrue(self.disp.valido(tok))
        self.assertFalse(self.disp.valido(tok + "x"))
        self.assertEqual(self.par.tentar(c)["erro"], "sem_codigo")  # uma vez so

    def test_codigo_nao_vai_pro_tablet(self):
        self.par.pedir()
        self.assertNotIn("codigo", self.par.estado(local=False))

    def test_disco_guarda_so_hash(self):
        self.par.pedir()
        tok = self.par.tentar(self.codigo())["token"]
        txt = self.disp.arquivo.read_text()
        self.assertNotIn(tok, txt)
        self.assertEqual(self.disp.arquivo.stat().st_mode & 0o777, 0o600)

    def test_expira(self):
        self.par.pedir()
        c = self.codigo()
        self.rel.t += acesso.CODIGO_VALIDADE + 1
        self.assertEqual(self.par.tentar(c)["erro"], "sem_codigo")

    def test_pedir_de_novo_repete_o_vigente(self):
        self.par.pedir()
        c = self.codigo()
        self.rel.t += 5
        self.par.pedir()
        self.assertEqual(self.codigo(), c)
        self.assertEqual(len(self.avisos), 1)

    def test_intervalo_entre_codigos(self):
        self.par.pedir()
        self.par.tentar(self.codigo())
        self.assertEqual(self.par.pedir()["erro"], "espera")
        self.rel.t += acesso.PEDIDO_INTERVALO
        self.assertTrue(self.par.pedir()["ok"])

    def test_erros_queimam_o_codigo(self):
        self.par.pedir()
        c = self.codigo()
        for i in range(acesso.CODIGO_ERROS):
            r = self.par.tentar(f"{(int(c) + 1) % 10 ** 6:06d}")
            self.assertEqual(r["erro"], "errado")
        self.assertEqual(r["restam"], 0)
        self.assertEqual(self.par.tentar(c)["erro"], "sem_codigo")  # o certo nao vale mais

    def test_trava_global(self):
        for _ in range(acesso.TRAVA_ERROS):
            self.rel.t += acesso.PEDIDO_INTERVALO
            if self.codigo() is None:
                self.par.pedir()
            r = self.par.tentar(self.errado())
        self.assertEqual(r["erro"], "travado")
        self.assertEqual(self.par.pedir()["erro"], "travado")
        self.rel.t += acesso.TRAVA_JANELA
        self.assertTrue(self.par.pedir()["ok"])

    def test_revoga(self):
        self.par.pedir()
        tok = self.par.tentar(self.codigo(), "tablet")["token"]
        self.rel.t += acesso.PEDIDO_INTERVALO
        self.par.pedir()
        tok2 = self.par.tentar(self.codigo(), "outro")["token"]
        ids = [i["id"] for i in self.disp.lista()]
        self.assertEqual(len(ids), 2)
        # Outro processo (a linha de comando) revoga: este rele o arquivo sozinho
        outro = acesso.Dispositivos(self.disp.arquivo, relogio=self.rel)
        self.assertEqual(outro.revoga(ids[0]), 1)
        self.assertFalse(self.disp.valido(tok))
        self.assertTrue(self.disp.valido(tok2))


def porta_livre():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class PontaAPonta(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        home = Path(cls.tmp.name)
        cfg = home / ".config/toca-do-texugo"
        cfg.mkdir(parents=True)
        cls.porta = porta_livre()
        (cfg / "config.json").write_text(json.dumps({"porta": cls.porta, "pareamento_local": False, "escuta": "0.0.0.0"}))
        env = {**os.environ, "HOME": str(home), "PATH": "/usr/bin:/bin"}
        cls.proc = subprocess.Popen([sys.executable, str(REPO / "server.py")], env=env, cwd=home,
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for _ in range(100):
            try:
                socket.create_connection(("127.0.0.1", cls.porta), 0.2).close()
                break
            except OSError:
                time.sleep(0.1)
        else:
            cls.proc.kill()
            raise RuntimeError("server.py nao subiu: " + cls.proc.stdout.read())

    @classmethod
    def tearDownClass(cls):
        cls.proc.kill()
        cls.proc.wait()
        cls.tmp.cleanup()

    def req(self, metodo, rota, corpo=None, cookie=None, host=None, dash=True):
        c = http.client.HTTPConnection("127.0.0.1", self.porta, timeout=5)
        h = {"Host": host or f"127.0.0.1:{self.porta}"}
        if dash and metodo == "POST":
            h["X-Dash"] = "1"
        if cookie:
            h["Cookie"] = cookie
        if corpo is not None:
            corpo = json.dumps(corpo)
            h["Content-Type"] = "application/json"
        c.request(metodo, rota, corpo, h)
        r = c.getresponse()
        return r, r.read()

    def test_caminho_do_tablet(self):
        r, b = self.req("GET", "/")
        self.assertEqual(r.status, 200)
        self.assertIn(b"parear", b)                      # sem cookie, a raiz e a tela de pareamento
        self.assertNotIn(b"renderDashB", b)
        self.assertEqual(self.req("GET", "/api/stats")[0].status, 401)
        self.assertEqual(self.req("POST", "/api/run/mute")[0].status, 401)
        self.assertEqual(self.req("GET", "/fontes/nao-existe.woff2")[0].status, 404)  # fonte e aberta

        self.assertEqual(self.req("POST", "/api/parear/pedir", dash=False)[0].status, 403)  # sem X-Dash
        r, b = self.req("POST", "/api/parear/pedir")
        self.assertEqual(r.status, 200, b)
        codigo = json.loads(self.req("GET", "/api/parear")[1])["codigo"]
        self.assertRegex(codigo, r"^\d{6}$")

        r, b = self.req("POST", "/api/parear", {"codigo": f"{(int(codigo) + 1) % 10 ** 6:06d}"})
        self.assertEqual(r.status, 403)
        self.assertEqual(json.loads(b)["erro"], "errado")

        r, b = self.req("POST", "/api/parear", {"codigo": codigo})
        self.assertEqual(r.status, 200, b)
        sc = r.getheader("Set-Cookie")
        self.assertIn("HttpOnly", sc)
        self.assertIn("SameSite=Strict", sc)
        cookie = sc.split(";", 1)[0]
        self.assertEqual(self.req("POST", "/api/parear", {"codigo": codigo})[0].status, 403)  # uso unico

        r, b = self.req("GET", "/", cookie=cookie)
        self.assertIn(b"renderDashB", b)                 # agora e o painel
        self.assertEqual(self.req("GET", "/api/version", cookie=cookie)[0].status, 200)
        self.assertEqual(self.req("GET", "/api/stats", cookie="toca=forjado")[0].status, 401)

        # SSE: chegam os dois eventos
        c = http.client.HTTPConnection("127.0.0.1", self.porta, timeout=5)
        c.request("GET", "/api/eventos", headers={"Host": f"127.0.0.1:{self.porta}", "Cookie": cookie})
        r = c.getresponse()
        self.assertEqual(r.status, 200)
        self.assertTrue(r.getheader("Content-Type").startswith("text/event-stream"))
        vistos, fim = set(), time.time() + 4
        while vistos != {"stats", "texugo"} and time.time() < fim:
            linha = r.fp.readline().decode()
            if linha.startswith("event: "):
                vistos.add(linha[7:].strip())
            elif linha.startswith("data: "):
                json.loads(linha[6:])
        r.close()  # so o c.close() deixa o socket aberto pelo arquivo da resposta
        c.close()
        self.assertEqual(vistos, {"stats", "texugo"})
        self._confere_aparelhos(cookie)

    def _confere_aparelhos(self, cookie):
        self.assertIn(b"aparelhos", self.req("GET", "/aparelhos")[1])
        v = json.loads(self.req("GET", "/api/aparelhos")[1])
        self.assertIn("codigo", v["pareamento"])
        item = v["aparelhos"][-1]
        self.assertEqual(item["ip"], "127.0.0.1")
        self.assertNotIn("hash", item)

        # SSE aberto aparece na lista, e fechado some
        c = http.client.HTTPConnection("127.0.0.1", self.porta, timeout=5)
        c.request("GET", "/api/eventos", headers={"Host": f"127.0.0.1:{self.porta}", "Cookie": cookie})
        r = c.getresponse()
        r.fp.readline()
        achado = lambda: next(a for a in json.loads(self.req("GET", "/api/aparelhos")[1])["aparelhos"]
                              if a["id"] == item["id"])
        # (o SSE fechado antes so cai na proxima escrita do servidor, ate 1 s depois)
        fim = time.time() + 3
        while achado()["sse"] != 1 and time.time() < fim:
            time.sleep(0.1)
        self.assertEqual(achado()["sse"], 1)

        self.assertEqual(self.req("POST", "/api/aparelhos/revoga", {"id": item["id"]}, dash=False)[0].status, 403)
        self.assertEqual(self.req("POST", "/api/aparelhos/revoga", {})[0].status, 400)
        self.assertEqual(json.loads(self.req("POST", "/api/aparelhos/revoga", {"id": item["id"]})[1])["revogados"], 1)
        self.assertEqual(self.req("GET", "/api/version", cookie=cookie)[0].status, 401)  # vale na hora
        r.close()
        c.close()

    def test_aparelhos_so_no_pc(self):
        """De fora do loopback a administracao nao existe, nem com o aparelho pareado."""
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            try:
                s.connect(("10.255.255.255", 1))
                ip = s.getsockname()[0]
            except OSError:
                self.skipTest("sem interface fora do loopback")
        if ip.startswith("127."):
            self.skipTest("sem interface fora do loopback")
        h = {"Host": f"{ip}:{self.porta}", "X-Dash": "1", "Content-Type": "application/json"}
        for metodo, rota, corpo in (("GET", "/aparelhos", None), ("GET", "/api/aparelhos", None),
                                    ("POST", "/api/aparelhos/revoga", '{"todos":true}')):
            c = http.client.HTTPConnection(ip, self.porta, timeout=5)
            c.request(metodo, rota, corpo, h)
            self.assertEqual(c.getresponse().status, 404, rota)
            c.close()

    def test_host_estranho(self):
        self.assertEqual(self.req("GET", "/", host=f"evil.com:{self.porta}")[0].status, 403)
        self.assertEqual(self.req("POST", "/api/parear/pedir", host=f"evil.com:{self.porta}")[0].status, 403)


if __name__ == "__main__":
    unittest.main(verbosity=2)
