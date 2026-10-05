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

- [x] ~~Fases 0 a 6: commit das pendências, infra dos layouts, gráfico de uso, radiais,
      temperaturas e consumo~~ (aab47c1…a62a5ce)
- [ ] Fase 7 — vazão: rede e disco em gráfico espelhado, escalas separadas
- [ ] Fase 8 — capacidade: discos + OneDrive em barras usado/total
- [ ] Fase 9 — tela de configuração: escolher quais medidores entram, ordem e largura
      (edita `painel.widgets` no localStorage; o registro `WIDGETS` já foi feito pra isso)

## Agenda e TODOs pelo Telegram

Decidido 2026-10-05: entrada pelo Telegram (sem OAuth, sem Google Cloud); marcar como feito
pelo toque no painel. O estado de "feito" é local — o Telegram é só entrada, o painel nunca
escreve de volta.

- [ ] A1 — `agenda.py`: `getUpdates` com offset persistido, **filtro por `chat_id`** (bot é
      público: qualquer um manda mensagem), parse simples de data, estado em JSON
- [ ] A2 — rotas `GET /api/agenda` e `POST /api/agenda/<id>/feito` (exige `X-Dash`, como os atalhos)
- [ ] A3 — widget "agenda": compromissos com hora em cima, recados sem hora embaixo; toque marca feito
- [ ] A4 — `agenda.exemplo.json` + README (token fica em `~/.config/toca-do-texugo/`, nunca no repo)

## Ideias / talvez

- Cravar o minuto do reset do Claude lendo o horário das mensagens em `~/.claude/projects/*.jsonl`
  em vez do meio entre duas amostras (ganho de ~5 min; não pega uso feito pelo app/web)
- Automatizar o destravamento do congelamento por composição (toggle de tela cheia do `wmctrl`)
- Fazer modelos (temas/layouts) de dashboard com inspiração em fotos do Pinterest
  (catálogo das referências em `.claude/context/DESIGN-REFS.md`)
