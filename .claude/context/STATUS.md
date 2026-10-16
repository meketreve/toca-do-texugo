---
updated: 2026-10-16
tier: 2
---

# Status — tier 2+

## Estado atual

Painel em uso no monitor virtual (DP-0), com o clássico e o agrupado por grade, editor de grade
completo e agenda do Telegram ligada. **Novo: o cérebro do texugo** (`texugo.py`) — rede de spike
com STDP que escolhe o comportamento do mascote no lugar da tabela de probabilidades. Nasce em
modo `instinto`; a chave está no medidor "Cérebro", que sai do catálogo do editor. Aprende desde
o boot nos dois modos e guarda os pesos em `~/.config/toca-do-texugo/texugo-cerebro.json`.
O catálogo do editor agora é agrupado (Máquina, Rede e disco, Texugo, Dia), com cabeçalho que
abre e fecha e contador de quantos medidores do grupo ainda estão fora do painel. O medidor
Cérebro ganhou um 2º estilo, **Perfis**: a situação preferida de cada comportamento em palavras,
a surpresa (z) do neurônio agora e, no topo, qual sensor está puxando o comando. E os medidores
viraram **perfis nomeados** (`painel.perfis`): "Jogo" e "Noite" com grades diferentes, trocando
pela página de atalhos. `atualizar-painel.sh` traz tudo isso pra máquina do painel.

## Próxima fase

O medidor Cérebro tem 3 estilos: Matriz (peso cru), Perfis (o que aprendeu, em palavras) e
**Rede** (`index.html:2162`) — a representação clássica: 16 sensores à esquerda, 6 comportamentos
à direita, 96 sinapses com grossura e opacidade do peso, e as ativações piscando em cima. São
DUAS camadas, sem oculta. Julgar na parede qual dos três fica no layout.

Depois disso, o que resta pede uso, não teclado:

1. **Rodar o cérebro alguns dias** e ver que personalidade aparece — o medidor Cérebro no estilo
   Perfis agora diz em palavras o que cada neurônio aprendeu, então dá pra julgar sem ler peso.
   Se as preferências não saírem do lugar em uma semana, subir o `ETA_STDP` (hoje 0.004).
2. **Decidir se a tela de configuração por botões sai** (`renderConfig`), já que o editor de grade
   faz o mesmo e agora os dois mexem no perfil ativo.
3. **Página "cuidar do texugo"** (tamagotchi) é a próxima coisa grande, se for pra ter uma — com a
   decisão de 2026-10-15 valendo: fome/sono viram SENSORES, nunca recompensa.

Antes de qualquer uma: `git merge` do `main-3ouquh` no `main` e `bash atualizar-painel.sh` na
máquina do painel — são 5 commits que ainda não rodaram em lugar nenhum, e o
`texugo.py` mudou (publica `inib`), então o restart é obrigatório.

## Pendências e bloqueios

- `docs/painel.png` do README é de antes: não mostra a linha do Claude, os layouts novos nem o
  cérebro. Um print novo expõe as porcentagens reais de uso — decidir se vale atualizar.
- Painel ainda pode congelar por parada de composição do Chrome (2026-10-01): `bash abrir-painel.sh`
  destrava (reposiciona e dá o toggle de tela cheia); nada automatizado.
- Se o `kick.com/api/v2` fechar, não há plano B — a API oficial não devolve seguidores.

## Concluído (recente)

- Estilo Rede no medidor Cérebro e bancada de testes portada pro repo (`testes/`) (2026-10-16)
- Perfis de layout: conjuntos nomeados de medidores, com migração do formato antigo (2026-10-16)
- `atualizar-painel.sh`: puxa o `main`, reinicia só se mudou `.py`, volta sozinho se não subir (2026-10-16)
- Catálogo do editor agrupado e estilo Perfis no medidor Cérebro (2026-10-16)
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
