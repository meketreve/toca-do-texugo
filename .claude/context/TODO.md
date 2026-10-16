---
updated: 2026-10-16
tier: 2
active: true
---

# TODO

## Agora

Os perfis acabaram. O que sobrou aqui depende de rodar e olhar, não de escrever código.

- [ ] Tema Linha na parede: toque na Agenda e na chave do Cérebro pelo Moonlight, cinza no tablet
- [ ] Tema Grafite na parede: toque na barra lateral e nas abas pelo Moonlight, claro no tablet
- [ ] Escolher na parede qual estilo do Cérebro fica: Matriz, Perfis, Rede ou Cards
- [ ] Juntar "Layout do painel" e "Perfil de medidores" numa linha só (perfil só vale no Agrupado)
- [ ] Rodar o cérebro alguns dias e ver que personalidade aparece (ajustar `ETA_STDP` se ficar
      rápido ou lento demais; hoje é 0.004 por disparo)
- [ ] Decidir se a tela de configuração por botões sai, agora que o editor de grade faz o mesmo

## Depois

- [ ] Decidir se atualiza o `docs/painel.png` (linha do Claude, layouts novos, cérebro)
- [ ] Se o `kick.com/api/v2` fechar, decidir o plano B (a API oficial não tem seguidores)
- [ ] Decidir se o `AGENTS.md` (cópia do `CLAUDE.md`) fica versionado ou vai pro `.gitignore`

## Concluído

- [x] ~~Tema Linha: os dois mockups de `~/Downloads` como tema + dois perfis de medidores, com a
      Barlow Condensed vendorizada em `fontes/` e servida pelo `server.py`~~
- [x] ~~Estilo Rede no Cérebro (duas camadas, sinapses pelo peso, ativação ao vivo) e
      bancada de testes em `testes/`~~
- [x] ~~Perfis de layout: `{nome: [medidores]}` em `painel.perfis`, troca pela página de atalhos,
      cria/apaga no editor e migração do `painel.widgets` antigo~~
- [x] ~~Perfis no medidor Cérebro: estilo "Perfis" com a situação preferida em palavras, a surpresa
      de cada neurônio e quem está puxando o comando~~
- [x] ~~Grupos no catálogo do editor: campo `grupo` no `regWidget`, cabeçalho que abre e fecha e
      contador de quantos ainda estão fora do painel~~
- [x] ~~Seletor de estilo no editor, no lugar do botão que ciclava; mostra "não cabe" e o tamanho
      que o estilo exige~~
- [x] ~~Camada de medidor: `medidor()`/`ESTILOS_MEDIDOR`, itens declarados uma vez~~
- [x] ~~Cérebro do texugo: `texugo.py` com STDP, medidor "Cérebro" e chave cérebro/instinto~~
- [x] ~~Editor de grade G1 a G4~~ (2a99716…bc507f0)
- [x] ~~Agenda e TODOs pelo Telegram, A1 a A4 + bot ligado~~ (07c9eb9)
- [x] ~~Layout "Agrupado" inteiro, com seletor e tela de configuração~~ (aab47c1…524063e)

## Ideias / talvez

- **Página "cuidar do texugo"** (tamagotchi): página própria no painel pra cuidar do bicho — fome,
  sono, carinho, limpeza, e o estado dele mudando com o tempo. Cuidado com o conflito: a decisão
  de 2026-10-15 é que afagar NÃO treina a rede (STDP sem recompensa). Caminho que preserva isso:
  as necessidades viram **sensores** novos do cérebro, não recompensa — o bicho fica com fome e a
  rede aprende sozinha o que fazer com isso, em vez de a gente premiar o comportamento certo
- Dar ao cérebro um comportamento que hoje não existe (cavar? olhar pro card que disparou?), pra
  ver a rede descobrir quando usar
- Cravar o minuto do reset do Claude lendo o horário das mensagens em `~/.claude/projects/*.jsonl`
- Automatizar o destravamento do congelamento por composição (hoje é `bash abrir-painel.sh`)
- Inspiração visual pros perfis de layout: fotos do Pinterest catalogadas em `DESIGN-REFS.md`

