#!/usr/bin/env python3
"""Duas paginas no MESMO localStorage: a 1a mexe nos perfis, a 2a so olha depois de recarregar."""
import pathlib
REPO = str(pathlib.Path(__file__).resolve().parent.parent)
AQUI = str(pathlib.Path(__file__).resolve().parent)
import pathlib, sys

SP = pathlib.Path(__file__).resolve().parent / "_saida"
SP.mkdir(exist_ok=True)
src = pathlib.Path(sys.argv[1]).read_text()

SONDA = """<script>
window.__erros = [];
window.addEventListener("error", e => window.__erros.push(String(e.message)));
</script>
"""

COMUM = """
const r = { passos: [] };
const esboco = () => ({
  ativo: perfilAtual(),
  perfis: Object.fromEntries(Object.entries(perfis()).map(([k, v]) => [k, v.map(i => i.id)])),
  natela: [...document.querySelectorAll("#widgets-b .widget")].map(c => c.dataset.w),
  chips: [...document.querySelectorAll("#ed-perfis .chip")].map(b => b.textContent),
  // a lista da pagina de atalhos e de TELAS desde 2026-10-16: o classico + um botao por perfil
  botoes: [...document.querySelectorAll("#telas button .lb")].map(b => b.textContent),
});
const conta = (passo) => r.passos.push({ passo, ...esboco() });
const fim = () => {
  r.erros = window.__erros;
  const pre = document.createElement("pre");
  pre.id = "relatorio"; pre.textContent = JSON.stringify(r);
  document.body.appendChild(pre);
};
"""

FASE1 = COMUM + """
try {
  localStorage.clear();
  // Formato ANTIGO: um conjunto so, e com as formas velhas que o normaliza() aceita
  localStorage.setItem("painel.widgets", JSON.stringify(["uso", { id: "temperaturas", col: 3 },
                                                        { id: "agenda", x: 6, y: 4, w: 6, h: 2 }]));
  localStorage.setItem("painel.layout", "agrupado");
  montarDashB(); renderConfig(); renderTelas();
  conta("migracao do formato antigo");

  edAbre();
  conta("editor aberto");

  novoPerfil("Jogo");
  conta("criou Jogo (copia do atual)");

  // Jogo fica diferente: tira a agenda e poe o cerebro
  salvarB(layoutB().filter(i => i.id !== "agenda"));
  salvarB([...layoutB(), { id: "cerebro", estilo: "perfis", x: 0, y: 3, w: 6, h: 3 }]);
  conta("Jogo mexido");

  setPerfil("Padrão");
  conta("voltou pro Padrão");

  novoPerfil("Noite");
  apagarPerfil("Noite");
  conta("criou e apagou Noite");

  setPerfil("Jogo");
  conta("deixou em Jogo pra recarregar");
} catch (e) { r.estouro = String(e && e.stack || e); }
fim();
"""

FASE2 = COMUM + """
try {
  conta("depois de recarregar");
  setPerfil("Padrão");
  conta("trocou pro Padrão na página nova");
  // Apagar o ultimo nao pode: tira os dois outros e tenta
  apagarPerfil("Jogo");
  conta("apagou Jogo");
  apagarPerfil("Padrão");
  conta("tentou apagar o último");
} catch (e) { r.estouro = String(e && e.stack || e); }
fim();
"""

for nome, roteiro in (("teste-perfis-1.html", FASE1), ("teste-perfis-2.html", FASE2)):
    out = src.replace("<head>", "<head>" + SONDA, 1).replace("</body>", "<script>" + roteiro + "</script></body>", 1)
    (SP / nome).write_text(out)
print("fases 1 e 2 prontas")
