---
updated: 2026-10-12
tier: 2
active: true
---

# TODO

## Agora

- [ ] Decidir se a tela de configuração por botões sai, agora que o editor de grade faz o mesmo
      (e se o editor é só pra usar do PC, com o tablet só exibindo)

## Depois

- [ ] Decidir se atualiza o `docs/painel.png` com a linha do Claude e os layouts novos
      (o print mostra uso real)
- [ ] Se o `kick.com/api/v2` fechar, decidir o plano B (a API oficial não tem seguidores)
- [ ] Decidir se o `AGENTS.md` (cópia do `CLAUDE.md`) fica versionado ou vai pro `.gitignore`

## Concluído

- [x] ~~Editor de grade G1 a G4: grade `{id, x, y, w, h}`, catálogo lateral, mover, redimensionar,
      tamanho mínimo, estilos alternativos e limite da tela~~ (2a99716…bc507f0)
- [x] ~~Agenda e TODOs pelo Telegram, A1 a A4 + bot criado e `agenda.json` preenchido~~ (07c9eb9)
- [x] ~~Layout "Agrupado" inteiro, com seletor e tela de configuração~~ (aab47c1…524063e;
      referências em `DESIGN-REFS.md`)

## Ideias / talvez

- Cravar o minuto do reset do Claude lendo o horário das mensagens em `~/.claude/projects/*.jsonl`
  em vez do meio entre duas amostras (ganho de ~5 min; não pega uso feito pelo app/web)
- Automatizar o destravamento do congelamento por composição (hoje é `bash abrir-painel.sh`)
- Fazer modelos (temas/layouts) de dashboard com inspiração em fotos do Pinterest
  (catálogo das referências em `.claude/context/DESIGN-REFS.md`)

