---
updated: 2026-10-05
tier: 2
active: true
---

# TODO

<!-- TETO: 60 linhas fora de blocos auto. Riscar o que terminou; o `git log` guarda o resto. -->
<!-- Importado só enquanto active: true. Ao terminar a tarefa, voltar p/ false. -->

## Agora

- [x] ~~Pôr o slug do canal no `redes.json` e conferir o card~~ (feito; card com número real)
- [ ] Commitar limites do Claude + troca do Instagram pela Kick (`server.py`, `redes.py`, `index.html`, `README.md`)

## Depois

- [ ] Decidir se atualiza o `docs/painel.png` com a linha do Claude (o print mostra uso real)
- [ ] Se o `kick.com/api/v2` fechar, decidir o plano B (a API oficial não tem seguidores)

## Layout alternativo do painel: agrupar por tipo de dado

Decidido 2026-10-05: **não substitui nada** — é um 2º layout do painel, escolhido na página de
atalhos e lembrado no `localStorage`. Gráfico de uso com linhas de 60 s + mín/máx na legenda; um
radial por peça (CPU e GPU); RAM/VRAM nos dois blocos (% no uso, GB na capacidade). Referências em
`DESIGN-REFS.md`. Tudo em `index.html`, sem mexer no `server.py` (os dados já existem).

- [x] ~~Fase 0 — commitar os 4 arquivos pendentes~~ (aab47c1)
- [x] ~~Fase 1 — infra: `page-dash-b`, registro `WIDGETS`, seletor nos atalhos, `render()` dividido~~
- [ ] Fase 2 — helpers: `drawMulti`, `drawGauge`, `norm(valor, teto)`, `faixa(hist)`
- [ ] Fase 3 — bloco "Uso": 1 gráfico, 4 linhas (CPU/RAM/GPU/VRAM)
- [ ] Fase 4 — radiais de CPU e GPU (arcos: uso, potência, temperatura, ventoinha, encoder)
- [ ] Fase 5 — temperaturas juntas numa escala 0–100 °C com zonas
- [ ] Fase 6 — potência: barra empilhada CPU+GPU, teto = TDP + limite
- [ ] Fase 7 — vazão: rede e disco em gráfico espelhado, escalas separadas
- [ ] Fase 8 — capacidade: discos + OneDrive em barras usado/total
- [ ] Fase 9 — tela de configuração: escolher quais medidores entram, ordem e largura
      (edita `painel.widgets` no localStorage; o registro `WIDGETS` já foi feito pra isso)

## Ideias / talvez

- Cravar o minuto do reset do Claude lendo o horário das mensagens em `~/.claude/projects/*.jsonl`
  em vez do meio entre duas amostras (ganho de ~5 min; não pega uso feito pelo app/web)
- Automatizar o destravamento do congelamento por composição (toggle de tela cheia do `wmctrl`)
- Fazer modelos (temas/layouts) de dashboard com inspiração em fotos do Pinterest
  (catálogo das referências em `.claude/context/DESIGN-REFS.md`)
