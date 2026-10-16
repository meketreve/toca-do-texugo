#!/usr/bin/env python3
"""Copia do index.html com dado real do texugo.py e roteiro que desenha os dois estilos do Cerebro."""
import pathlib
REPO = str(pathlib.Path(__file__).resolve().parent.parent)
AQUI = str(pathlib.Path(__file__).resolve().parent)
import json, pathlib, sys

SP = pathlib.Path(__file__).resolve().parent / "_saida"
SP.mkdir(exist_ok=True)
src = pathlib.Path(sys.argv[1]).read_text()
novo = json.loads((SP / "texugo-novo.json").read_text())
velho = json.loads((SP / "texugo-velho.json").read_text())

SONDA = """<script>
window.__erros = [];
window.addEventListener("error", e => window.__erros.push(String(e.message)));
</script>
"""

ROTEIRO = """<script>
const CASOS = { novo: __NOVO__, velho: __VELHO__ };
const r = { passos: [] };
const leia = el => [...el.querySelectorAll(".cb-pf:not(.cb-pfcab)")].map(p => ({
  nm: p.querySelector(".nm").textContent,
  ativo: p.classList.contains("ativo"),
  larg: p.querySelector(".z i").style.width,
  z: p.querySelector(".zv").textContent,
  sit: p.querySelector(".sit").textContent,
  vazio: p.querySelector(".sit").classList.contains("vazio"),
}));
try {
  const estilos = WIDGETS.cerebro.estilos.map(e => e.id);
  r.estilos = estilos;
  for (const caso of ["novo", "velho"]) {
    texugoData = CASOS[caso];
    for (const eid of estilos) {
      const e = WIDGETS.cerebro.estilos.find(x => x.id === eid);
      const box = document.createElement("div");
      document.body.appendChild(box);
      e.montar(box);
      e.render(box, {});
      e.render(box, {});   // 2a passada: o estilo nao pode remontar nada
      const p = { caso, estilo: eid,
                  topo: box.querySelector(".cb-comp").textContent,
                  puxa: box.querySelector(".cb-puxa").textContent,
                  idade: box.querySelector(".cb-idade").textContent };
      if (eid === "perfis") p.linhas = leia(box);
      else p.celulas = box.querySelectorAll(".cb-cel").length;
      r.passos.push(p);
      // O ultimo caso fica na tela, num card de verdade, pra tirar o print
      if (caso === "velho") {
        document.querySelectorAll("body > *:not(script)").forEach(x => { if (x !== box) x.hidden = true; });
        box.className = "card";
        box.style.cssText = "width:900px;height:360px;margin:30px;padding:14px 18px";
        box.insertAdjacentHTML("afterbegin", `<h2>Cérebro — ${eid}</h2>`);
      } else box.remove();
    }
  }
} catch (e) { r.estouro = String(e && e.stack || e); }
r.erros = window.__erros;
const pre = document.createElement("pre");
pre.id = "relatorio";
pre.textContent = JSON.stringify(r);
document.body.appendChild(pre);
</script>
"""

ROTEIRO = ROTEIRO.replace("__NOVO__", json.dumps(novo)).replace("__VELHO__", json.dumps(velho))
out = src.replace("<head>", "<head>" + SONDA, 1).replace("</body>", ROTEIRO + "</body>", 1)
(SP / "teste-cerebro.html").write_text(out)
print("teste-cerebro.html pronto")
