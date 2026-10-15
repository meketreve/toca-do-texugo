---
updated: 2026-10-15
tier: 2
---

# Status — tier 2+

## Estado atual

Painel em uso no monitor virtual (DP-0), com o clássico e o agrupado por grade, editor de grade
completo e agenda do Telegram ligada. **Novo: o cérebro do texugo** (`texugo.py`) — rede de spike
com STDP que escolhe o comportamento do mascote no lugar da tabela de probabilidades. Nasce em
modo `instinto`; a chave está no medidor "Cérebro", que sai do catálogo do editor. Aprende desde
o boot nos dois modos e guarda os pesos em `~/.config/toca-do-texugo/texugo-cerebro.json`.

## Próxima fase

Deixar rodando alguns dias e ver que personalidade aparece — o teste sintético mostra as 4
situações escolhendo neurônios bem sintonizados (53–78% contra 17% de acaso), mas com os sinais
reais do painel isso ainda não foi observado ao longo do tempo.
→ verify: medidor Cérebro com contraste visível na matriz (vínculos fortes contornados) depois de
algumas horas, e `curl -s 127.0.0.1:8787/api/texugo` com as 6 taxas perto de 4 Hz e nenhum limiar
grudado em 0,1 ou 60.

## Pendências e bloqueios

- `docs/painel.png` do README é de antes: não mostra a linha do Claude, os layouts novos nem o
  cérebro. Um print novo expõe as porcentagens reais de uso — decidir se vale atualizar.
- Painel ainda pode congelar por parada de composição do Chrome (2026-10-01): `bash abrir-painel.sh`
  destrava (reposiciona e dá o toggle de tela cheia); nada automatizado.
- Se o `kick.com/api/v2` fechar, não há plano B — a API oficial não devolve seguidores.

## Concluído (recente)

- Cérebro do texugo: STDP + covariância + homeostase, medidor e chave de modo (2026-10-15)
- Projeto movido de volta pro SSD; service, autostart e lançador do menu corrigidos (2026-10-12)
- `core.hooksPath .githooks` religado neste clone — o `pre-commit` estava desligado (2026-10-12)
- Agenda do Telegram ligada: bot no @BotFather e `agenda.json` preenchido (2026-10-12)
- Editor de grade G1 a G4, com estilos por medidor e grade limitada à tela (bc507f0…2a99716)
- Agenda e recados no painel, alimentados por um bot do Telegram (07c9eb9)

<!-- auto:start -->
data: 2026-10-12

```
26c6213 chore: contexto do projeto e AGENTS.md
bc507f0 Grade limitada à tela: o painel nunca passa do que cabe
f7b0d2d Estilos alternativos por medidor: o mesmo dado como barra ou número
c10f87e Tamanho mínimo por medidor e linha de altura fixa
2a99716 Editor de grade: catálogo à esquerda, canvas de 12 colunas à direita
07c9eb9 Agenda e recados no painel, alimentados por um bot do Telegram
3e3cb06 Anota o editor de grade com arrastar e soltar e enxuga o TODO
524063e Tela de configuração dos medidores do layout agrupado
--- status ---
 M .claude/context/LEARNINGS.md
 M .claude/context/MAP.md
 M .claude/context/STATUS.md
 M .claude/context/TODO.md
```
<!-- auto:end -->
