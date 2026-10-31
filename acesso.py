#!/usr/bin/env python3
"""Acesso de fora do PC: filtro de rede, Host e pareamento do tablet por codigo.

O painel pode escutar na LAN/Tailscale (config.json -> "escuta") e ser aberto direto no navegador
do tablet. Tres barreiras, nesta ordem:

1. Cliente: so loopback, rede privada (10/8, 172.16/12, 192.168/16) e Tailscale (100.64/10 e
   fd7a:115c:a1e0::/48). IP publico nao passa nem do primeiro byte.
2. Host: IP literal, `localhost` ou um nome listado em "hosts" -- nome desconhecido e DNS
   rebinding (um site qualquer apontando o proprio dominio pro IP do PC).
3. Pareamento: o tablet pede um codigo, o PC mostra (notify-send, journal e /parear no proprio
   PC). Seis digitos, 120 s, uma vez so, 5 erros por codigo e 10 erros por hora no total travam o
   pareamento por uma hora. Quem acerta ganha um token de 256 bits em cookie HttpOnly; no disco
   fica so o sha256 dele (dispositivos.json), entao o arquivo vazado nao abre o painel.

Linha de comando (nao sobe o servidor):

    python3 acesso.py lista            # aparelhos pareados
    python3 acesso.py revoga <id>      # tira um (o id e o comeco do hash, como a lista mostra)
    python3 acesso.py revoga-todos

No proprio PC, a mesma coisa em tela: http://127.0.0.1:8787/aparelhos (codigo vigente, aparelhos,
quem esta conectado agora e revogar). Essa rota so existe pra loopback.

O servidor rele o arquivo quando ele muda: revogar vale na hora, sem reiniciar.
"""
import hashlib
import hmac
import ipaddress
import json
import os
import secrets
import sys
import threading
import time
from pathlib import Path

DISPOSITIVOS = Path.home() / ".config/toca-do-texugo/dispositivos.json"
COOKIE = "toca"
TOKEN_VIDA = 365 * 86400
NOME_MAX = 200          # o User-Agent cortado antes disso perde a versao do navegador
CODIGO_VALIDADE = 120   # s
CODIGO_ERROS = 5        # erros num codigo e ele queima
TRAVA_ERROS = 10        # erros no total, dentro da janela, e o pareamento trava
TRAVA_JANELA = 3600     # s: janela dos erros e tempo da trava
PEDIDO_INTERVALO = 10   # s entre dois codigos novos (segura o spam de notificacao)
VISTO_GRAVA = 600       # s entre duas gravacoes do "visto por ultimo"

REDES_OK = [ipaddress.ip_network(n) for n in ("100.64.0.0/10", "fd7a:115c:a1e0::/48")]


def _ip(ip):
    try:
        a = ipaddress.ip_address(ip.split("%", 1)[0])
    except ValueError:
        return None
    if a.version == 6 and a.ipv4_mapped:
        a = a.ipv4_mapped
    return a


def eh_local(ip):
    a = _ip(ip)
    return bool(a and a.is_loopback)


def cliente_ok(ip):
    """Loopback, rede privada ou Tailscale. O resto (IP publico, lixo) fica de fora."""
    a = _ip(ip)
    if a is None or a.is_multicast or a.is_unspecified:
        return False
    return a.is_loopback or a.is_private or any(a in n for n in REDES_OK)


def host_ok(host, porta, extras=()):
    """Header Host: IP literal, localhost ou nome configurado, sempre na porta do servidor."""
    host = (host or "").strip().lower()
    if host.startswith("["):
        nome, _, resto = host[1:].partition("]")
        p = resto[1:] if resto.startswith(":") else ("" if not resto else None)
    else:
        nome, _, p = host.rpartition(":") if ":" in host else (host, "", "")
    if p is None or p != str(porta):
        return False
    if nome == "localhost" or nome in {e.lower() for e in extras}:
        return True
    return _ip(nome) is not None


def cookie_token(header):
    """Token do cookie `toca` no header Cookie (sem SimpleCookie: ele engasga com cookie alheio)."""
    for parte in (header or "").split(";"):
        k, _, v = parte.strip().partition("=")
        if k == COOKIE and v:
            return v
    return None


def set_cookie(token):
    return f"{COOKIE}={token}; Max-Age={TOKEN_VIDA}; Path=/; HttpOnly; SameSite=Strict"


def _hash(token):
    return hashlib.sha256(token.encode()).hexdigest()


class Dispositivos:
    """Aparelhos pareados: {sha256 do token: {nome, criado, visto}} em dispositivos.json."""

    def __init__(self, arquivo=DISPOSITIVOS, relogio=time.time):
        self.arquivo = Path(arquivo)
        self.relogio = relogio
        self._lock = threading.Lock()
        self._itens, self._mtime, self._gravado = {}, None, 0
        self._sse = {}  # sha256 do token: conexoes SSE abertas agora (so em memoria)
        self._le()

    def _le(self):
        try:
            mtime = self.arquivo.stat().st_mtime_ns
        except OSError:
            self._itens, self._mtime = {}, None
            return
        if mtime == self._mtime:
            return
        try:
            v = json.loads(self.arquivo.read_text())
            self._itens = {k: d for k, d in v.items() if isinstance(d, dict)} if isinstance(v, dict) else {}
        except (OSError, ValueError):
            self._itens = {}
        self._mtime = mtime

    def _grava(self):
        self.arquivo.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.arquivo.with_suffix(".tmp")
        fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w") as f:
            f.write(json.dumps(self._itens, ensure_ascii=False, indent=2) + "\n")
        os.replace(tmp, self.arquivo)
        self._mtime = self.arquivo.stat().st_mtime_ns
        self._gravado = self.relogio()

    def cria(self, nome):
        token = secrets.token_urlsafe(32)
        agora = int(self.relogio())
        with self._lock:
            self._le()
            self._itens[_hash(token)] = {"nome": (nome or "?")[:NOME_MAX], "criado": agora, "visto": agora}
            self._grava()
        return token

    def valido(self, token, ip=None, nome=None):
        """Confere o token e anota por onde o aparelho veio (`ip`, `nome`: o User-Agent de agora)."""
        if not token or len(token) > 100:
            return False
        h = _hash(token)
        with self._lock:
            self._le()
            d = self._itens.get(h)
            if d is None:
                return False
            agora = self.relogio()
            if agora - d.get("criado", 0) > TOKEN_VIDA:
                return False
            d["visto"] = int(agora)
            if ip:
                d["ip"] = ip
            if nome:
                d["nome"] = nome[:NOME_MAX]
            if agora - self._gravado > VISTO_GRAVA:
                self._grava()
            return True

    def sse(self, token, delta):
        """Conta as conexoes SSE abertas do aparelho (+1 ao abrir, -1 ao fechar)."""
        if not token:
            return
        h = _hash(token)
        with self._lock:
            n = self._sse.get(h, 0) + delta
            if n > 0:
                self._sse[h] = n
            else:
                self._sse.pop(h, None)

    def lista(self):
        with self._lock:
            self._le()
            return [{"id": h[:8], **d, "sse": self._sse.get(h, 0)}
                    for h, d in sorted(self._itens.items(), key=lambda x: x[1].get("criado", 0))]

    def revoga(self, prefixo=None):
        """Tira um aparelho pelo comeco do hash (ou todos, sem prefixo). Devolve quantos sairam."""
        with self._lock:
            self._le()
            fora = [h for h in self._itens if prefixo is None or h.startswith(prefixo)]
            if prefixo is not None and len(fora) > 1:
                return -len(fora)  # prefixo ambiguo: nao tira nenhum
            for h in fora:
                del self._itens[h]
            if fora:
                self._grava()
            return len(fora)


class Pareamento:
    """Um codigo por vez: pedir() gera (ou repete o vigente), tentar() troca o codigo por token."""

    def __init__(self, dispositivos, avisar=None, relogio=time.time):
        self.disp = dispositivos
        self.avisar = avisar or (lambda codigo: None)
        self.relogio = relogio
        self._lock = threading.Lock()
        self._codigo = None      # (codigo, expira, erros)
        self._pedido = -1e9
        self._erros = []         # instantes dos erros, pra trava
        self._trava = 0

    def _vigente(self, agora):
        if self._codigo and agora >= self._codigo[1]:
            self._codigo = None
        return self._codigo

    def _travado(self, agora):
        self._erros = [t for t in self._erros if agora - t < TRAVA_JANELA]
        return max(0, self._trava - agora)

    def estado(self, local=False):
        """O que a tela de pareamento mostra. O codigo em si so vai pro proprio PC."""
        with self._lock:
            agora = self.relogio()
            c = self._vigente(agora)
            out = {"travado": round(self._travado(agora)), "expira": round(c[1] - agora) if c else 0}
            if local:
                out["codigo"] = c[0] if c else None
            return out

    def pedir(self):
        with self._lock:
            agora = self.relogio()
            trava = self._travado(agora)
            if trava:
                return {"erro": "travado", "travado": round(trava)}
            c = self._vigente(agora)
            if c is None:
                if agora - self._pedido < PEDIDO_INTERVALO:
                    return {"erro": "espera", "espera": round(PEDIDO_INTERVALO - (agora - self._pedido))}
                c = self._codigo = (f"{secrets.randbelow(10 ** 6):06d}", agora + CODIGO_VALIDADE, 0)
                self._pedido = agora
                novo = True
            else:
                novo = False
            expira = round(c[1] - agora)
        if novo:
            self.avisar(c[0])
        return {"ok": True, "expira": expira}

    def tentar(self, codigo, nome=""):
        """Token novo, ou {"erro": ...}. Codigo certo vale uma vez; errado conta pros dois limites."""
        codigo = str(codigo or "").strip()
        with self._lock:
            agora = self.relogio()
            trava = self._travado(agora)
            if trava:
                return {"erro": "travado", "travado": round(trava)}
            c = self._vigente(agora)
            if c is None:
                return {"erro": "sem_codigo"}
            if len(codigo) == 6 and hmac.compare_digest(codigo, c[0]):
                self._codigo = None
                certo = True
            else:
                certo = False
                self._erros.append(agora)
                erros = c[2] + 1
                self._codigo = None if erros >= CODIGO_ERROS else (c[0], c[1], erros)
                if len(self._erros) >= TRAVA_ERROS:
                    self._trava, self._codigo, self._erros = agora + TRAVA_JANELA, None, []
                    return {"erro": "travado", "travado": TRAVA_JANELA}
                return {"erro": "errado", "restam": CODIGO_ERROS - erros if self._codigo else 0}
        if certo:
            return {"token": self.disp.cria(nome)}


def _cli(args):
    d = Dispositivos()
    if args[:1] == ["lista"]:
        itens = d.lista()
        for i in itens:
            quando = lambda t: time.strftime("%Y-%m-%d %H:%M", time.localtime(t))
            print(f"{i['id']}  pareado {quando(i['criado'])}  visto {quando(i['visto'])}  {i['nome']}")
        if not itens:
            print("nenhum aparelho pareado")
        return 0
    if args[:1] == ["revoga"] and len(args) == 2:
        n = d.revoga(args[1])
        print({0: "nenhum aparelho com esse id"}.get(n, f"{n} aparelho revogado" if n > 0 else
                                                     f"id ambiguo ({-n} aparelhos): use mais caracteres"))
        return 0 if n > 0 else 1
    if args[:1] == ["revoga-todos"]:
        print(f"{d.revoga()} aparelho(s) revogado(s)")
        return 0
    print("uso: python3 acesso.py lista | revoga <id> | revoga-todos", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(_cli(sys.argv[1:]))
