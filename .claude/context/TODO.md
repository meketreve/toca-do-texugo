---
updated: 2026-10-16
tier: 2
active: true
---

# TODO

## Agora

O que sobrou aqui depende de rodar e olhar, não de escrever código.

- [ ] Na parede: escolher a tela e o tema, e conferir a **barra lateral nos três temas** pelo
      Moonlight (alvos de 48 px, item ativo e ponto de conexão; no Atual ela é nova)
- [ ] No Linha, pelo Moonlight: toque nos itens da Agenda e na chave do Cérebro, cinza no tablet
- [ ] Escolher qual estilo do Cérebro fica: Matriz, Perfis, Rede ou Cards (Cards pede 7×3)
- [ ] Rodar o cérebro alguns dias e ver que personalidade aparece (ajustar o `ETA_STDP` — 0,004 —
      se ficar rápido ou lento demais)
- [ ] Decidir se a tela de configuração por botões sai, agora que o editor de grade faz o mesmo

## Depois

- [ ] Decidir se atualiza o `docs/painel.png` (linha do Claude, temas novos, cérebro)
- [ ] Se o `kick.com/api/v2` fechar, decidir o plano B (a API oficial não tem seguidores)
- [ ] Decidir se o `AGENTS.md` (cópia do `CLAUDE.md`) fica versionado ou vai pro `.gitignore`

## Concluído

- [x] ~~"Tela do painel": layout e perfil numa lista só~~, e ~~carretel do Disco com giro suave~~
- [x] ~~Tema Linha: os dois mockups como tema e dois perfis de medidores, Barlow vendorizada~~
- [x] ~~Barra lateral nos três temas, no lugar do botão discreto de página~~
- [x] ~~Estilo Rede no Cérebro e bancada de testes em `testes/`~~
- [x] ~~Perfis de layout, grupos no catálogo do editor e estilos por medidor~~
- [x] ~~Cérebro do texugo: `texugo.py` com STDP, medidor "Cérebro" e chave cérebro/instinto~~
- [x] ~~Editor de grade G1 a G4~~ (2a99716…bc507f0)
- [x] ~~Agenda e TODOs pelo Telegram, A1 a A4 + bot ligado~~ (07c9eb9)
- [x] ~~Layout "Agrupado" inteiro, com seletor e tela de configuração~~ (aab47c1…524063e)

## Ideias / talvez

- **Página "cuidar do texugo"** (tamagotchi): fome, sono, carinho e limpeza como **sensores** novos
  do cérebro, nunca recompensa (decisão de 2026-10-15) — o bicho fica com fome e a rede aprende
  sozinha o que fazer com isso, em vez de a gente premiar o comportamento certo
- Dar ao cérebro um comportamento que hoje não existe (cavar? olhar pro card que disparou?), pra
  ver a rede descobrir quando usar
- Cravar o minuto do reset do Claude lendo o horário das mensagens em `~/.claude/projects/*.jsonl`
- Automatizar o destravamento do congelamento por composição (hoje é `bash abrir-painel.sh`)
- Inspiração visual pros perfis de tela: fotos do Pinterest catalogadas em `DESIGN-REFS.md`
