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

# A fixture do perfil tem que existir ANTES do localStorage que o roteiro injeta: ela e uma copia
# MINIMA do que o app semeia com o tema Linha. O que se testa aqui e o TEMA seguindo o perfil
# escolhido; o desenho da tela do Linha o `teste-linha-2.html` cobre.
PERFIL_LINHA_FIXO = {"Linha · Dados": [{"id": "vazao-rede", "x": 0, "y": 0, "w": 4, "h": 3}]}

# Uma tela por arquivo. Com tema Linha o painel semeia sozinho os dois perfis do mockup no boot;
# sem ele nem mexe em `painel.perfis`, pra o painel cair no "Padrão" de sempre.
# `clica_tema`/`clica_perfil` sao testes de ponta a ponta: a 1a carga clica no botao (o mesmo
# caminho do dedo), o `setTema()` recarrega e e a pagina RECARREGADA que reporta -- de graca, no
# mesmo arquivo (por isso a semente so limpa o localStorage na primeira carga).
TELAS = [
    dict(arquivo="teste-linha-1.html", tema="linha", layout="agrupado", perfil="Linha · Máquina"),
    dict(arquivo="teste-linha-2.html", tema="linha", layout="agrupado", perfil="Linha · Dados"),
    dict(arquivo="teste-atual.html", layout="classico"),
    dict(arquivo="teste-agrupado.html", layout="agrupado"),
    dict(arquivo="teste-grafite.html", tema="grafite", layout="classico"),
    dict(arquivo="teste-tema.html", layout="classico", clica_tema="linha"),
    dict(arquivo="teste-perfil-tema.html", layout="agrupado", perfil="Padrão",
         perfis=PERFIL_LINHA_FIXO, clica_perfil="Linha · Dados"),
    # a barra lateral levando pras paginas, e o aviso de volta que agora aparece nos tres temas
    dict(arquivo="teste-atalhos.html", layout="agrupado", clica_rail="2"),
    dict(arquivo="teste-atalhos-linha.html", tema="linha", layout="agrupado",
         perfil="Linha · Máquina", clica_rail="2"),
    # a combinacao da parede: tema Linha com o layout classico escolhido -- a pagina vira grade,
    # e era aqui que a grade ficava montada e sem desenho
    dict(arquivo="teste-linha-classico.html", tema="linha", layout="classico", perfil="Linha · Máquina"),
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
TROCA_TEMA = """<script>
setTimeout(() => { document.querySelector('#temas button:nth-child(__N__)').click(); }, 1200);
</script>
"""
# Mesma coisa pelo seletor de PERFIL: escolher "Linha · Dados" com outro tema ligado tem que
# ligar o tema do perfil, senao a tela sai com a fonte e as cores erradas.
TROCA_PERFIL = """<script>
setTimeout(() => {
  const b = [...document.querySelectorAll("#perfis button")].find(x => x.querySelector(".lb").textContent === "__NOME__");
  if (b) b.click();
}, 1200);
</script>
"""
# E pela barra lateral, que e a navegacao de todos os temas (o botao discreto de pagina saiu)
TROCA_RAIL = """<script>
setTimeout(() => { document.querySelector('#rail button[data-ir="__N__"]').click(); }, 1200);
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
    // Barra lateral: tem que estar visivel em TODOS os temas, com um botao marcado, e o botao
    // discreto de trocar pagina (o `#pager`) nao pode mais existir no documento
    r.pagina = [page, PAGES[page], !document.getElementById("volta").hidden &&
                getComputedStyle(document.getElementById("volta")).display !== "none"];
    r.rail = { visivel: getComputedStyle(document.getElementById("rail")).display !== "none",
               botoes: [...document.querySelectorAll("#rail button")].map(b => b.dataset.ir + (b.classList.contains("on") ? "*" : "")),
               pager: !!document.getElementById("pager") };
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
    // Quanto cada cartao desenhou: cartao montado e nunca desenhado fica com o corpo vazio, e o
    // relatorio de erro nao pega isso (o renderDashB engole a excecao, e sem desenho nao ha erro)
    r.desenho = [...document.querySelectorAll("#widgets-b .widget")]
      .map(c => [c.dataset.w, c.querySelector(".w-body").innerHTML.length]);
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
    // Texugo: em que cartoes ele pode pisar e onde ele esta agora. `spriteTopo` negativo = o bicho
    // esta com o corpo fora da tela por cima.
    r.plataformas = platforms().map(e => [e.dataset.w || String(e.className), Math.round(e.getBoundingClientRect().top)]);
    // Em pe em cada uma delas: o corpo (MH acima das patas) tem que caber na tela
    r.mascoteEmPe = platforms().map(e => {
      const S = spot(e);
      return [e.dataset.w || "card", Math.round(S.top - MH), S.top - MH >= 0];
    });
    r.mascote = { estado: M.state, pe: Math.round(M.y), spriteTopo: Math.round(M.y - MH),
                  cartao: (M.el && M.el.dataset.w) || "", fora: M.y - MH < 0 };
  } catch (e) { r.estouro = String(e && e.stack || e); }
  const pre = document.createElement("pre");
  pre.id = "relatorio"; pre.textContent = JSON.stringify(r, null, 1);
  document.body.appendChild(pre);
}, __ESPERA__);
</script>
"""

def monta(arquivo, tema, layout, perfil, perfis, clica_tema=None, clica_perfil=None, clica_rail=None, dados=None):
    tema_js = "" if not tema or tema == "atual" else f'localStorage.setItem("painel.tema", "{tema}");'
    # O perfil ativo e o que a tela mostra: sem ele o painel cairia no "Padrão" (o perfil de
    # nascenca), e nao na tela do mockup que `ativaLinha()` deixa ativa ao ligar o tema.
    perfil_js = f'localStorage.setItem("painel.perfil", "{perfil}");' if perfil else ""
    perfis_js = f'localStorage.setItem("painel.perfis", JSON.stringify({json.dumps(perfis, ensure_ascii=False)}));' if perfis else ""
    semente = (SEMENTE.replace("__DADOS__", json.dumps(dados or DADOS, ensure_ascii=False))
                      .replace("__TEMA__", tema_js).replace("__LAYOUT__", layout)
                      .replace("__PERFIL__", perfil_js + perfis_js))
    # 5200 ms: o roteiro so mede depois que a fonte trocou, senao mede o layout do fallback
    roteiro = ROTEIRO.replace("__ESPERA__", "5200")
    if clica_tema:
        extra = TROCA_TEMA.replace("__N__", str(TEMAS_ORDEM.index(clica_tema) + 1))
    elif clica_perfil:
        extra = TROCA_PERFIL.replace("__NOME__", clica_perfil)
    elif clica_rail:
        extra = TROCA_RAIL.replace("__N__", str(clica_rail))
    else:
        extra = ""
    out = (src.replace("<head>", "<head>" + semente, 1)
              .replace("</body>", extra + roteiro + "</body>", 1))
    (SP / arquivo).write_text(out)


for tela in TELAS:
    monta(tela["arquivo"], tela.get("tema"), tela["layout"], tela.get("perfil"), tela.get("perfis"),
          tela.get("clica_tema"), tela.get("clica_perfil"), tela.get("clica_rail"))
print("telas prontas:", ", ".join(t["arquivo"] for t in TELAS))

# `--real`: as duas telas do Linha com o dado da PROPRIA maquina do painel, em vez da fixture. E o
# que reproduz o que se ve na parede -- a fixture tem numeros redondos e nao pega campo que so
# existe no dado de verdade (gpu nula, volume mudo, disco nao montado, cota do OneDrive em falta).
if "--real" in sys.argv:
    import urllib.request
    real = {k: json.load(urllib.request.urlopen(f"http://127.0.0.1:8787/api/{k}", timeout=5))
            for k in ("stats", "texugo", "agenda", "redes")}
    real["shortcuts"] = []
    monta("teste-real-1.html", "linha", "agrupado", "Linha · Máquina", None, dados=real)
    monta("teste-real-2.html", "linha", "agrupado", "Linha · Dados", None, dados=real)
    monta("teste-real-3.html", "linha", "classico", "Linha · Máquina", None, dados=real)
    print("telas com o dado real: teste-real-1.html, teste-real-2.html, teste-real-3.html")
