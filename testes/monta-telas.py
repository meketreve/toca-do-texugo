#!/usr/bin/env python3
"""Copias do index.html com um /api falso e um tema/layout por arquivo, pro print comparar.

O que se olha aqui e o DESENHO dos cartoes com dado conhecido, sem depender da maquina do painel:
um `fetch` falso serve um /api/stats com os numeros do mockup (11% de CPU, 20% de GPU, 44/39/55
graus, 15+37 W de 265), o /api/texugo do `estado.py` e uma agenda de exemplo. O roteiro espera o
primeiro render e larga um relatorio no DOM; e o print (`--screenshot`) que compara com o mockup.

As duas telas do tema Linha sao o alvo, mas as outras tres (Atual classico, Atual agrupado e
Grafite) entram de graca no mesmo roteiro: xerife de regressao dos temas que NAO mudaram.

    python3 testes/monta-telas.py index.html
    python3 -m http.server 8799 --bind 127.0.0.1 --directory testes/_saida &
    google-chrome --headless=new --window-size=1920,1080 --virtual-time-budget=6000 \
      --screenshot=/tmp/linha-1.png http://127.0.0.1:8799/teste-linha-1.html

O print usa 1920x1080 de proposito: o Chrome redimensiona a PAGINA pro tamanho do print, entao o
viewport vira 1080 (que e o monitor do painel) e os numeros batem com o mockup. Ja o relatorio,
que roda numa pagina so, pede `--window-size=1920,1167` (o Chrome desconta ~87 px de janela).
"""
import json
import pathlib
import shutil
import subprocess
import sys

AQUI = pathlib.Path(__file__).resolve().parent
REPO = AQUI.parent
SP = AQUI / "_saida"
SP.mkdir(exist_ok=True)
src = pathlib.Path(sys.argv[1]).read_text()

# A fonte do tema Linha e servida em /fontes/ pelo servidor de verdade; aqui a copia viaja junto
shutil.copytree(REPO / "fontes", SP / "fontes", dirs_exist_ok=True)

# Cerebro de verdade: o mesmo `estado.py` do teste do Cérebro (gera na primeira vez)
CEREBRO = SP / "texugo-velho.json"
if not CEREBRO.exists():
    CEREBRO.write_text(subprocess.run([sys.executable, str(AQUI / "estado.py"), "20"],
                                      capture_output=True, text=True, check=True).stdout)

GiB = 1024 ** 3
STATS = {
    "t": 1776380000,
    "uptime": 9 * 3600 + 36 * 60,
    "load": [3.8, 3.1, 2.4],
    "cpu": {"pct": 11.4, "per": [11 + (i % 7) for i in range(24)], "freq": 1370,
            "temp": 44, "threads": 24, "power": 15, "tdp": 105},
    "mem": {"used": 11 * GiB, "total": 32 * GiB, "pct": 35, "swap_used": GiB, "swap_total": 8 * GiB},
    "gpu": {"util": 20, "enc": 0, "dec": 0, "mem_used": 1229, "mem_total": 6144, "temp": 39,
            "power": 37, "power_limit": 160, "fan": 34, "clock": 1365,
            "name": "NVIDIA GeForce RTX 2060"},
    "nvme_temp": 55,
    "disks": [{"mount": "/", "label": "SSD", "used": 430e9, "total": 954e9, "pct": 45},
              {"mount": "/mnt/nvme", "label": "NVME", "used": 29e9, "total": 468e9, "pct": 6}],
    "diskio": {"read": 0, "write": 316 * 1024},
    "net": {"iface": "wlp3s0", "rx": 14 * 1024, "tx": 1.7 * 1024 * 1024},
    "procs": [],
    "volume": {"pct": 65, "muted": False},
    "onedrive": {"state": "synced", "quota": {"used": 0.7e9, "total": 5e9}},
    "media": {"player": "spotify", "status": "Playing", "title": "Hardtekk Baby - Slowed",
              "artist": "N!GHTvisiøn", "album": "Hardtekk Baby", "position": 93, "length": 116},
    "claude": {"t": 1776380000, "five_hour": 42, "week": 18},
}
AGENDA = {"ligado": True, "itens": [
    {"id": "1", "texto": "Reunião com o editor", "quando": 1776384000, "feito": False},
    {"id": "2", "texto": "Responder comentários do vídeo", "quando": 1776300000, "feito": False},
    {"id": "3", "texto": "Gravar intro da live", "quando": 1776550000, "feito": False},
    {"id": "4", "texto": "Pagar a internet", "quando": 1776290000, "feito": True},
    {"id": "5", "texto": "Trocar pasta térmica da GPU", "quando": None, "feito": False},
]}
REDES = {"youtube": {"configured": True, "ok": True, "followers": 4321, "seg": "inscritos", "live": False},
         "twitch": {"configured": True, "ok": True, "followers": 812, "seg": "seguidores",
                    "live": True, "espectadores": 34, "jogo": "Retro"}}

DADOS = {"stats": STATS, "agenda": AGENDA, "redes": REDES, "shortcuts": [],
         "texugo": json.loads(CEREBRO.read_text())}

# tema + layout por arquivo. Com tema Linha o roteiro tambem semeia os dois perfis do mockup;
# sem ele nem mexe em `painel.perfis`, pra o painel cair no "Padrão" de sempre.
# O ultimo arquivo e o teste de ponta a ponta: a 1a carga limpa o localStorage, a 2a (depois do
# reload que o `setTema()` dispara) ja reporta com o tema trocado -- de graca, no mesmo arquivo.
TELAS = [
    ("teste-linha-1.html", "linha", "agrupado", "Linha · Máquina", None),
    ("teste-linha-2.html", "linha", "agrupado", "Linha · Dados", None),
    ("teste-atual.html", "atual", "classico", None, None),
    ("teste-agrupado.html", "atual", "agrupado", None, None),
    ("teste-grafite.html", "grafite", "classico", None, None),
    ("teste-tema.html", None, "classico", None, "linha"),
]

# Ordem dos botoes na pagina de atalhos -- tem que casar com `TEMAS` no index.html; se mudar,
# o teste do tema cai em outro botao e o relatorio acusa (o `tema` que chega nao e o esperado).
TEMAS_ORDEM = ["atual", "grafite", "grafite-claro", "linha"]

# Antes de TUDO (inclusive do <script> do tema, que le o localStorage): tema, perfil e o /api falso.
# O `sessionStorage` marca que esta e a primeira carga: no teste do tema a pagina RECARREGA no meio
# (e o `setTema()` que recarrega), e limpar o localStorage de novo apagaria a troca que se quer ver.
SEMENTE = """<script>
window.__erros = [];
window.addEventListener("error", e => window.__erros.push(String(e.message)));
try {
  if (!sessionStorage.getItem("carga")) { localStorage.clear(); sessionStorage.setItem("carga", "1"); }
  __TEMA__
  localStorage.setItem("painel.layout", "__LAYOUT__");
  __PERFIL__
} catch (e) {}
const DADOS = __DADOS__;
const resp = d => ({ ok: true, json: async () => d });
window.fetch = url => {
  const u = String(url).split("?")[0];
  const chave = { "/api/stats": "stats", "/api/texugo": "texugo", "/api/agenda": "agenda",
                  "/api/redes": "redes", "/api/shortcuts": "shortcuts" }[u];
  if (chave) return Promise.resolve(resp(DADOS[chave]));
  if (u === "/api/version") return Promise.resolve(resp({ index: 1 }));
  return Promise.resolve(resp({}));
};
</script>
"""

# Na tela do teste de tema, a primeira carga clica no botao do tema (o mesmo caminho do dedo:
# `setTema()` grava, ativa o perfil e recarrega) e e a pagina RECARREGADA que reporta.
TROCA = """<script>
setTimeout(() => { document.querySelector('#temas button:nth-child(__N__)').click(); }, 1200);
</script>
"""

ROTEIRO = """<script>
setTimeout(() => {
  const r = { erros: window.__erros };
  try {
    const vb = document.getElementById("widgets-b");
    r.janela = [innerWidth, innerHeight];
    r.tema = document.documentElement.dataset.tema || "atual";
    r.classes = document.documentElement.className;
    r.layout = layout;
    r.perfil = perfilAtual();
    r.perfis = Object.keys(perfis());
    r.linhas = LINHAS;
    r.fonte = [document.fonts.status, document.fonts.check('300 20px "Barlow Condensed"')];
    r.cabecalho = getComputedStyle(document.querySelector("header")).display;
    r.sondas = [];
    // Sonda: re-renderiza cada medidor SEM o try/catch do painel, senao erro de desenho passa
    // calado (o renderDashB engole) e o cartao fica com o ultimo desenho bom, parecendo certo.
    for (const [id, m] of montados) {
      try { m.e.render(m.body, DADOS.stats); } catch (e) { r.sondas.push(id + ": " + (e && e.message)); }
    }
    r.cartoes = [...document.querySelectorAll("#widgets-b .widget")].map(c => {
      const q = c.getBoundingClientRect();
      return { w: c.dataset.w, estilo: c.dataset.estilo, x: Math.round(q.left), y: Math.round(q.top),
               largura: Math.round(q.width), altura: Math.round(q.height),
               rotulo: c.querySelector("h2").textContent, canto: (c.querySelector(".l-extra") || {}).textContent || "" };
    });
    // `rola` > cliente = o desenho passou do espaco do cartao (o .w-body corta, nao estoura a
    // tela). A folga de 3 px e das linhas fracionarias da grade, que arredondam pra cima.
    const estourou = m => m.body.scrollHeight > m.body.clientHeight + 3;
    r.estouros = [];
    for (const [id, m] of montados) if (estourou(m)) r.estouros.push([id, m.body.clientHeight, m.body.scrollHeight]);
    // Quem estourou, com as alturas dos filhos: sem isso so se sabe que estourou, nao onde
    r.estouroDetalhe = {};
    for (const [id, m] of montados) if (estourou(m)) {
      const raiz = m.body.firstElementChild;
      r.estouroDetalhe[id] = [raiz.className, Math.round(raiz.getBoundingClientRect().height),
        [...raiz.children].map(e => [e.className, Math.round(e.getBoundingClientRect().height)])];
    }
    const fora = document.getElementById("fora-aviso");
    r.foraDaTela = fora.hidden ? "" : fora.textContent;
  } catch (e) { r.estouro = String(e && e.stack || e); }
  const pre = document.createElement("pre");
  pre.id = "relatorio"; pre.textContent = JSON.stringify(r, null, 1);
  document.body.appendChild(pre);
}, __ESPERA__);
</script>
"""

for arquivo, tema, layout, perfil, troca in TELAS:
    tema_js = "" if not tema or tema == "atual" else f'localStorage.setItem("painel.tema", "{tema}");'
    # O perfil ativo e o que a tela mostra: sem ele o painel cairia no "Padrão" (o perfil de
    # nascenca), e nao na tela do mockup que `ativaLinha()` deixa ativa ao ligar o tema.
    perfil_js = f'localStorage.setItem("painel.perfil", "{perfil}");' if perfil else ""
    semente = (SEMENTE.replace("__DADOS__", json.dumps(DADOS, ensure_ascii=False))
                      .replace("__TEMA__", tema_js).replace("__LAYOUT__", layout).replace("__PERFIL__", perfil_js))
    # 5200 ms: o roteiro so mede depois que a fonte trocou, senao mede o layout do fallback
    roteiro = ROTEIRO.replace("__ESPERA__", "5200")
    extra = TROCA.replace("__N__", str(TEMAS_ORDEM.index(troca) + 1)) if troca else ""
    out = (src.replace("<head>", "<head>" + semente, 1)
              .replace("</body>", extra + roteiro + "</body>", 1))
    (SP / arquivo).write_text(out)
print("telas prontas:", ", ".join(a for a, *_ in TELAS))
