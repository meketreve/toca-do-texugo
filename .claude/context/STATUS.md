---
updated: 2026-10-16
tier: 2
---

# Status — tier 2+

## Estado atual

Painel em uso no monitor virtual (DP-0), servido por `server.py` em `127.0.0.1:8787`, com editor de
grade, agenda do Telegram, redes sociais e o **cérebro do texugo** (`texugo.py`, rede de spike com
STDP que escolhe o comportamento do mascote; pesos em `~/.config/toca-do-texugo/texugo-cerebro.json`).

Três temas, todos opção (`painel.tema`): **Atual** (o de sempre, intacto), **Grafite** (escuro e
claro, do mockup `Painel · Grafite`) e **Linha** (dos mockups `Linha · mostradores da máquina` e
`Linha · dados, música e texugo`: preto, traço fino, Barlow Condensed vendorizada em `fontes/` e
servida pelo próprio `server.py`). A **barra lateral** (`#rail`) é a navegação dos três temas; o
botão discreto de trocar página saiu.

Na página de atalhos a lista é de **telas**: "Clássico" (página fixa) mais uma entrada por perfil de
medidores da grade — trocar de tela grava layout e perfil juntos, e escolher uma tela do Linha liga
o tema Linha. No Linha o cabeçalho sai (vira o card Relógio) e os dois artboards entram como perfis
de 3×2 (`Linha · Máquina`, `Linha · Dados`), semeados na primeira vez que o tema liga.

## Próxima fase

Na parede: escolher a tela e o tema (atalhos), conferir a barra lateral nos três temas pelo
Moonlight (no Atual ela é nova — vale o toque nos cinco botões) e escolher o estilo do Cérebro que
fica (Matriz, Perfis, Rede, Cards — Cards pede 7×3). Depois disso só resta o que pede uso:

1. Rodar o cérebro alguns dias e ver que personalidade aparece (não saindo em uma semana, subir o
   `ETA_STDP`, hoje 0.004).
2. Decidir se `renderConfig` (a configuração por botões) sai, já que o editor de grade faz o mesmo.
3. Página "cuidar do texugo" (tamagotchi): fome/sono viram SENSORES, nunca recompensa (2026-10-15).

## Pendências e bloqueios

- `docs/painel.png` é de antes (sem a linha do Claude, sem os temas novos, sem o cérebro): um print
  novo expõe as porcentagens reais de uso — decidir se vale.
- O painel ainda pode congelar por parada de composição do Chrome (2026-10-01): `bash abrir-painel.sh`
  destrava; nada automatizado.
- Se o `kick.com/api/v2` fechar, não há plano B (a API oficial não devolve seguidores).

## Concluído (recente)

- Tema Linha: os dois artboards como perfis, com dois medidores novos (Relógio, Tocando agora) (2026-10-16)
- Barra lateral nos três temas, e a lista de telas no lugar do par layout+perfil (2026-10-16)
- Estilos novos por medidor (Encoders, Bancada, Faders, Faixa, Pratos, Cilindros) (2026-10-16)
- Cérebro do texugo: STDP + covariância + homeostase, medidor e chave de modo (2026-10-15)
- Perfis nomeados de medidores, catálogo do editor agrupado, estilos Perfis/Rede no Cérebro (2026-10-16)
- Bancada de testes portada pro repo (`testes/`) e `atualizar-painel.sh` (2026-10-16)
- Projeto de volta pro SSD; service, autostart e lançador do menu corrigidos (2026-10-12)
- Agenda do Telegram ligada e editor de grade G1 a G4 (2026-10-12)

<!-- auto:start -->
data: 2026-10-16

```
93fa1b5 "Tela do painel": layout e perfil viram uma lista só
f14d796 Três defeitos dos desenhos do Linha que só a parede mostrava
a179783 Quem manda no desenho é a página, não o layout: grade do Linha ficava sem dado
a0de9a6 Barra lateral em todos os temas, no lugar do botão discreto de página
7474032 O desenho do medidor não é do tema: perfil do Linha fora do Linha desenhava vazio
35e499c O texugo não pisa onde não cabe: fora a fileira de cima do tema Linha
4713205 Linha: as paginas de servico (atalhos, editor, redes) tambem entram no tom do tema
e1b5568 Tema Linha: as duas telas dos mockups, com a Barlow Condensed vendorizada
--- status ---
 M .claude/context/MAP.md
 M .claude/context/STATUS.md
 M .claude/context/TODO.md
```
<!-- auto:end -->
