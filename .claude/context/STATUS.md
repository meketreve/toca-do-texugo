---
updated: 2026-10-03
tier: 2
---

# Status — tier 2+

<!-- TETO: 60 linhas FORA do bloco auto (o bloco é do script e não conta). Resumir "Concluído" quando crescer. -->

## Estado atual

Painel em uso no monitor virtual: hardware, OneDrive, música com visualizador, redes sociais e o
texugo. Repo público e limpo de credenciais. Último commit é 0219986 (2026-09-19).
Na árvore de trabalho (**sem commit**): **limites do Claude** no cabeçalho (janela de 5 h e semanal,
reset estimado) e **Kick no lugar do Instagram** no card de redes — já configurada e mostrando
número real. Mexe em `server.py`, `redes.py`, `index.html` e `README.md`.

## Próxima fase

Commitar as duas funções (`server.py`, `redes.py`, `index.html`, `README.md`) — conferir antes
que nada pessoal vaza (o hook `.githooks/pre-commit` ajuda).
→ verify: `git status --short` sem os 4 arquivos; `curl -s 127.0.0.1:8787/api/redes` com `kick` sem erro.

## Pendências e bloqueios

- `docs/painel.png` do README é de antes e não mostra a linha do Claude. Um print novo expõe as
  porcentagens reais de uso — decidir se vale atualizar.
- Painel ainda pode congelar por parada de composição do Chrome (2026-10-01): destrava à mão com o
  toggle de tela cheia do `wmctrl` (receita em `BUGS.md`); nada automatizado.

## Concluído (recente)

- Slug da Kick posto no `redes.json`; card mostra seguidores reais (conferido 2026-10-03)
- Diagnóstico do congelamento por composição do Chrome registrado em `BUGS.md` (2026-10-01)
- Instagram saiu; Kick entrou no lugar, sem credencial (endpoint interno do site, via curl)
- Limites do Claude no cabeçalho, lidos de `~/.config/Claude/plan-usage-history.json` (só leitura)
- Chrome não congela mais o painel achando que a janela está oculta (0219986)
- Projeto renomeado pra Toca do Texugo e preparado pra repo público (936c068, 92362c1)

## Bruto do git (auto — não editar)

<!-- auto:start -->
data: 2026-10-03

```
0219986 Impede o Chrome de congelar o painel achando que ele está oculto
14b5f0d Nomes internos viram toca-do-texugo e prints novos com música tocando
936c068 Renomeia o projeto pra Toca do Texugo
8fa5e72 Licença MIT e link pro pc-streaming
92362c1 Prepara pra repo público: config da máquina fora do código, prints novos
16a9e97 Card do OneDrive embaixo dos discos
ceef862 README completo pro GitHub, com print do painel
2cdd3c2 Card Redes vira tabela: seguidores, +hoje, views e likes por rede
--- status ---
 M README.md
 M index.html
 M redes.py
 M server.py
?? .claude/
?? CLAUDE.md
```
<!-- auto:end -->
