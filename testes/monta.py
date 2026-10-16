#!/usr/bin/env python3
"""Monta uma copia do index.html com sonda de erro e roteiro de teste do catalogo."""
import pathlib
REPO = str(pathlib.Path(__file__).resolve().parent.parent)
AQUI = str(pathlib.Path(__file__).resolve().parent)
import pathlib
import sys

SP = pathlib.Path(__file__).resolve().parent / "_saida"
SP.mkdir(exist_ok=True)
src = pathlib.Path(sys.argv[1]).read_text()

SONDA = """<script>
window.__erros = [];
window.addEventListener("error", e => window.__erros.push(String(e.message)));
window.addEventListener("unhandledrejection", e => window.__erros.push("rejeicao: " + e.reason));
</script>
"""

ROTEIRO = """<script>
/* O editor escuta pointerdown. setPointerCapture com pointerId sintetico estoura
   NotFoundError e mataria o resto do handler -- aqui vira no-op. */
Element.prototype.setPointerCapture = function () {};
const toque = el => el.dispatchEvent(new PointerEvent("pointerdown", { bubbles: true, pointerId: 1 }));
const catalogo = () => [...document.getElementById("ed-cat").children].map(el => {
  if (el.dataset.grp) return { tipo: "grupo", id: el.dataset.grp, txt: el.textContent, cheio: el.classList.contains("cheio") };
  if (el.dataset.novo) return { tipo: "item", id: el.dataset.novo, off: !!el.disabled };
  return { tipo: "ajuda" };
}).filter(x => x.tipo !== "ajuda");
const canvas = () => [...document.querySelectorAll("#ed-canvas .ed-bloco .tit")].map(e => e.textContent);

const r = { linhas: null, passos: [] };
try {
  localStorage.clear();
  edAbre();
  r.linhas = LINHAS;
  r.passos.push({ passo: "abriu", cat: catalogo(), canvas: canvas() });

  const h = document.querySelector('[data-grp="maquina"]');
  toque(h);
  r.passos.push({ passo: "fecha maquina", cat: catalogo() });
  toque(document.querySelector('[data-grp="maquina"]'));
  r.passos.push({ passo: "reabre maquina", cat: catalogo() });

  // Grupo fechado tem de continuar fechado depois de por um medidor (o edRender refaz o catalogo)
  toque(document.querySelector('[data-grp="dia"]'));
  toque(document.querySelector('[data-novo="capacidade"]'));
  r.passos.push({ passo: "poe capacidade", cat: catalogo(), canvas: canvas(),
                  aviso: document.getElementById("ed-aviso").textContent });

  // Sem vaga: o aviso tem de aparecer e nada entra na grade
  toque(document.querySelector('[data-novo="cerebro"]'));
  r.passos.push({ passo: "poe cerebro (sem vaga?)", cat: catalogo(), canvas: canvas(),
                  aviso: document.getElementById("ed-aviso").textContent });

  // Grade vazia: aqui da pra ver o medidor entrando mesmo
  localStorage.setItem("painel.widgets", "[]");
  edAbre();
  r.passos.push({ passo: "grade vazia", cat: catalogo(), canvas: canvas() });
  toque(document.querySelector('[data-novo="cerebro"]'));
  r.passos.push({ passo: "poe cerebro na vazia", cat: catalogo(), canvas: canvas(),
                  aviso: document.getElementById("ed-aviso").textContent });

  regWidget("zz-sem-grupo", { nome: "Sem grupo", col: 3, h: 1, montar() {}, render() {} });
  edRender();
  r.passos.push({ passo: "medidor sem grupo", cat: catalogo() });
} catch (e) {
  r.estouro = String(e && e.stack || e);
}
r.erros = window.__erros;
const pre = document.createElement("pre");
pre.id = "relatorio";
pre.textContent = JSON.stringify(r);
document.body.appendChild(pre);
</script>
"""

out = src.replace("<head>", "<head>" + SONDA, 1).replace("</body>", ROTEIRO + "</body>", 1)
(SP / "teste.html").write_text(out)
print("teste.html pronto")
