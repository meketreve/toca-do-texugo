---
updated: 2026-10-05
tier: 2
active: true
---

# TODO

<!-- TETO: 60 linhas fora de blocos auto. Riscar o que terminou; o `git log` guarda o resto. -->
<!-- Importado só enquanto active: true. Ao terminar a tarefa, voltar p/ false. -->

## Agora

- [ ] Ligar a agenda: criar o bot e preencher o `agenda.json` (código todo pronto)

## Depois

- [ ] Decidir se atualiza o `docs/painel.png` com a linha do Claude (o print mostra uso real)
- [ ] Se o `kick.com/api/v2` fechar, decidir o plano B (a API oficial não tem seguidores)
- [x] ~~Layout "Agrupado" inteiro: 2º layout sem tirar nada do clássico, 8 medidores agrupados por
      tipo de dado, seletor e tela de configuração~~ (aab47c1…524063e; referências em `DESIGN-REFS.md`)

## Editor de grade com arrastar e soltar (objetivo maior)

Catálogo de medidores prontos à esquerda, canvas em grade à direita: arrastar do catálogo pro
canvas, reposicionar e redimensionar no lugar. Substitui os botões da tela de configuração atual
(que foram feitos assim por causa do toque impreciso via Moonlight — **decidir se o editor é só
pra usar do PC**, com o tablet só exibindo). Junto: mais estilos de exibição por medidor.

- [x] ~~G1 a G3 — grade `{id, x, y, w, h}`, catálogo lateral, mover e redimensionar no canvas~~
- [ ] Decidir se a tela de configuração por botões sai, agora que o editor faz o mesmo
- [ ] G4 — estilos alternativos por medidor (ex.: o mesmo dado como barra, anel ou número)

## Agenda e TODOs pelo Telegram

Decidido 2026-10-05: entrada pelo Telegram (sem OAuth, sem Google Cloud); marcar como feito
pelo toque no painel. O estado de "feito" é local — o Telegram é só entrada, o painel nunca
escreve de volta.

- [x] ~~A1 a A4: `agenda.py`, rotas, widget e documentação~~
- [ ] Criar o bot no @BotFather e pôr token + `chat_id` em `~/.config/toca-do-texugo/agenda.json`
      — só isso falta pra ligar (o painel mostra "sem bot configurado" até lá)

## Ideias / talvez

- Cravar o minuto do reset do Claude lendo o horário das mensagens em `~/.claude/projects/*.jsonl`
  em vez do meio entre duas amostras (ganho de ~5 min; não pega uso feito pelo app/web)
- Automatizar o destravamento do congelamento por composição (toggle de tela cheia do `wmctrl`)
- Fazer modelos (temas/layouts) de dashboard com inspiração em fotos do Pinterest
  (catálogo das referências em `.claude/context/DESIGN-REFS.md`)
