---
updated: 2026-10-15
tier: 2
active: true
---

# TODO

## Agora

Próxima sessão: perfis. O G4 (estilos de exibição por medidor) já está feito.

- [ ] **Perfis no medidor Cérebro**: ler melhor o que cada neurônio aprendeu — sensor ordenado por
      peso, "situação preferida" em palavras, quem está puxando o comando agora (`index.html:1681`)
- [ ] **Perfis de layout**: conjuntos nomeados de medidores ("jogo", "trabalho", "noite") e a troca
      entre eles; hoje só existe um, em `localStorage["painel.widgets"]` (`index.html:1077`/`1083`)
- [ ] Rodar o cérebro alguns dias e ver que personalidade aparece (ajustar `ETA_STDP` se ficar
      rápido ou lento demais; hoje é 0.004 por disparo)
- [ ] Decidir se a tela de configuração por botões sai, agora que o editor de grade faz o mesmo

## Depois

- [ ] Decidir se atualiza o `docs/painel.png` (linha do Claude, layouts novos, cérebro)
- [ ] Se o `kick.com/api/v2` fechar, decidir o plano B (a API oficial não tem seguidores)
- [ ] Decidir se o `AGENTS.md` (cópia do `CLAUDE.md`) fica versionado ou vai pro `.gitignore`

## Concluído

- [x] ~~Cérebro do texugo: `texugo.py` com STDP, medidor "Cérebro" e chave cérebro/instinto~~
- [x] ~~Editor de grade G1 a G4~~ (2a99716…bc507f0)
- [x] ~~Agenda e TODOs pelo Telegram, A1 a A4 + bot ligado~~ (07c9eb9)
- [x] ~~Layout "Agrupado" inteiro, com seletor e tela de configuração~~ (aab47c1…524063e)

## Ideias / talvez

- Dar ao cérebro um comportamento que hoje não existe (cavar? olhar pro card que disparou?), pra
  ver a rede descobrir quando usar
- Cravar o minuto do reset do Claude lendo o horário das mensagens em `~/.claude/projects/*.jsonl`
- Automatizar o destravamento do congelamento por composição (hoje é `bash abrir-painel.sh`)
- Inspiração visual pros perfis de layout: fotos do Pinterest catalogadas em `DESIGN-REFS.md`

