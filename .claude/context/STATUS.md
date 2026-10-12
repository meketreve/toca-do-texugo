---
updated: 2026-10-12
tier: 2
---

# Status — tier 2+

## Estado atual

Painel em uso no monitor virtual (DP-0), com dois layouts: o clássico e o agrupado por grade.
O editor de grade está completo (G1 a G4): catálogo à esquerda, canvas de 12 colunas, mover,
redimensionar, tamanho mínimo por medidor, estilos alternativos (anéis/barras/números) e grade
limitada ao que cabe na tela. A agenda pelo Telegram está **ligada** — bot criado, `agenda.json`
preenchido e item real chegando do celular. Repo público, limpo de credencial, árvore sem pendência
de código. O projeto voltou pra `/mnt/SSD/git-projeto/toca-do-texugo` (2026-10-12).

## Próxima fase

Decidir se a tela de configuração por botões (`renderConfig`, `index.html:1147`) sai agora que o
editor de grade (`index.html:1196`) faz o mesmo — e, junto, se o editor é só pra usar do PC, com o
tablet apenas exibindo (os botões existem por causa do toque impreciso via Moonlight).
→ verify: abrir `http://127.0.0.1:8787`, montar um layout no editor, recarregar e ver que a grade
voltou igual sem passar pela tela de botões.

## Pendências e bloqueios

- `docs/painel.png` do README é de antes e não mostra a linha do Claude nem os layouts novos. Um
  print novo expõe as porcentagens reais de uso — decidir se vale atualizar.
- Painel ainda pode congelar por parada de composição do Chrome (2026-10-01): `bash abrir-painel.sh`
  destrava (reposiciona e dá o toggle de tela cheia); nada automatizado.
- Se o `kick.com/api/v2` fechar, não há plano B — a API oficial não devolve seguidores.

## Concluído (recente)

- Projeto movido de volta pro SSD; service, autostart e lançador do menu corrigidos (2026-10-12)
- `core.hooksPath .githooks` religado neste clone — o `pre-commit` estava desligado (2026-10-12)
- Agenda do Telegram ligada: bot no @BotFather e `agenda.json` preenchido (2026-10-12)
- Editor de grade G1 a G4, com estilos por medidor e grade limitada à tela (bc507f0…2a99716)
- Agenda e recados no painel, alimentados por um bot do Telegram (07c9eb9)
- Layout "Agrupado" inteiro, com seletor e tela de configuração (aab47c1…524063e)
- Vazão espelhada de rede e disco, armazenamento num bloco só (da9e344)

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
