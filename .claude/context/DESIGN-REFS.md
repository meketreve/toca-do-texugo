---
updated: 2026-10-05
tier: 2
---

# Referências de design para o painel

Catálogo de exemplos de dashboard que serviram de inspiração: o que cada card mostra e **como**
mostra. Não é importado pelo `CLAUDE.md` — ler sob demanda, quando for mexer no layout do
`index.html`. Ligado à ideia "modelos de dashboard" do `TODO.md`.

---

## Ref 01 — Dashboard de estudo/produtividade (dark, roxo)

Fonte: pinterest.com/pin/5348093304858430 — "Productivity Workspace UI".
Imagem: `i.pinimg.com/736x/c5/6b/79/c56b7937407f8542e25b72f783676b5c.jpg` (736×1104).
Formato: retrato, mockup de app desktop em janela sem borda sobre papel de parede.

### Estrutura geral

- **Moldura**: janela escura arredondada sobre papel de parede (montanha roxa desfocada); os três
  botões de semáforo (vermelho/azul/azul) no canto superior esquerdo.
- **Grade**: coluna fixa de ícones à esquerda + conteúdo em grade de 12 colunas, cards de larguras
  diferentes na mesma linha (3 na primeira: 4/4/3). Gutter generoso (~16 px) e cantos bem
  arredondados (~16-20 px).
- **Cards**: superfície translúcida mais clara que o fundo, borda de 1 px em branco a ~8 %, sem
  sombra forte — o contraste vem do fundo quase preto. Efeito "vidro" deixa a montanha vazar nos
  cards da direita.
- **Dock flutuante** no rodapé, centralizado, pílula com 7 ícones coloridos (estilo macOS).

### Card a card

| # | Card | Informação | Como é apresentada |
|---|------|------------|--------------------|
| 1 | Saudação (topo esq.) | "Good Morning, **Alex** 👋" + lema "Focus · Plan · Execute · Succeed" | Tipografia grande (~34 px), nome em roxo claro na 2ª linha; emoji como ícone; lema em cinza pequeno com `·` separando |
| 2 | Relógio (topo dir.) | `07:45 AM` + "Tuesday, May 28, 2024" | Hora em display enorme (~56 px) com `:` em peso menor e "AM" pequeno ao lado em roxo; data em cinza abaixo, alinhada à direita |
| 3 | Sidebar | 7 ícones: home, calendário, tarefas, pastas, gráfico, histórico, config + lua (tema) no fim | Barra vertical estreita (~56 px), item ativo num quadrado roxo arredondado; resto em cinza; o toggle de tema isolado embaixo |
| 4 | Calendar | Mês de maio, dia 28 selecionado, dia 7 com ponto de evento | Grade 7×6 clássica; cabeçalho `‹ May 2024 ›`; dias de outro mês em cinza escuro; selecionado = círculo roxo cheio; evento = pontinho roxo sob o número |
| 5 | Today's Schedule | 4 compromissos: hora início/fim, título, subtítulo | Lista vertical de faixas; **barra colorida de 3 px à esquerda** por categoria (roxo/azul/laranja/verde); hora empilhada (início em cima, fim embaixo) na coluna da esquerda; bolinha da cor antes do título |
| 6 | Clima | 24°, "Partly Cloudy", máx ↑28° mín ↓18°, previsão de 3 dias | Ícone de nuvem/sol grande ilustrado; temperatura gigante com `°` menor; máx/mín com setas ↑↓ lado a lado; previsão em 3 colunas (dia / ícone pequeno / temperatura) |
| 7 | My Tasks | 5 tarefas, cada uma com prazo e favorito; filtros All/Today/Upcoming/Completed; botão `+ Add Task` | Abas em pílula (ativa com fundo roxo); linhas com checkbox circular (feita = círculo roxo cheio + texto riscado), prazo em cinza à direita, estrela de favorito no fim (preenchida só na 1ª) |
| 8 | Focus Timer | `25:00` + rótulo "Focus" | Anel de progresso circular com gradiente roxo→rosa sobre trilha escura; tempo no centro; botão ▶ roxo circular embaixo do anel e ícone de reset discreto ao lado |
| 9 | Upcoming Deadlines | 3 entregas: título, "Due in N days", data, prioridade; link "View All" | Linhas com ícone quadrado colorido por matéria (roxo/azul/laranja) à esquerda; prazo e data na mesma linha em cinza; **badge de prioridade** à direita em pílula vazada (High roxo, Medium azul/laranja) |
| 10 | Quick Notes | 4 anotações + rodapé motivacional; botão `+` | Lista de bullets simples (·), uma linha cada; frase "Keep going! You're doing great. 💜" centralizada no fim, separada por espaço |
| 11 | Study Playlist | Faixa "Lo-Fi Beats", artista "Chill & Focus" | Capa quadrada com ícone de nota musical; controles ⏮ ▶ ⏭ (play em círculo roxo preenchido); **visualizador de barras** à direita, barras finas em gradiente roxo |
| 12 | Habit Tracker | 4 hábitos × 7 dias, seletor "This Week" | Grade: nome do hábito com ícone colorido na esquerda, 7 colunas S–S; dia cumprido = círculo cheio com ✓ na cor do hábito, pendente = círculo vazado cinza; seletor em dropdown pequeno no cabeçalho |
| 13 | Dock | 7 atalhos (apps, pastas, calendário com dia 28, tarefas, timer, notas, lixeira) | Pílula flutuante translúcida; ícones coloridos estilo macOS; o do calendário mostra o número do dia real |

### Padrões que valem copiar

- **Um acento só** (roxo) carregando estado ativo, progresso e seleção; as outras cores servem só
  para categorizar (barra do schedule, ícone da matéria, cor do hábito).
- **Número grande, rótulo pequeno**: hora, temperatura e timer usam o mesmo truque — valor em
  display, unidade/rótulo em corpo pequeno e cinza.
- **Barra colorida à esquerda** para categorizar item de lista sem poluir com badge.
- **Círculo vazado vs. cheio** como vocabulário único de "pendente vs. feito" (tarefas e hábitos).
- **Badge em pílula vazada** (borda + texto na cor, fundo transparente) para prioridade.
- Hierarquia por peso e cor, não por borda: quase nada tem divisória; o que separa é o espaço.

### Paleta (amostrada da imagem, não estimada)

Medida pixel a pixel: tons chapados por frequência, acentos por pico de saturação em cada faixa de
matiz. "Vivo" é o pixel mais claro daquele matiz (o núcleo do elemento); "médio" é a média da faixa
(já com a mistura das bordas suavizadas).

| Papel | Hex | Onde aparece |
|---|---|---|
| Base / fora da janela | `#00000C` | preto azulado das margens |
| Superfície do card | `#0C1224` | todos os cards (tom mais frequente da imagem) |
| Superfície elevada | `#12182A` | abas, badges, dock, campo de busca |
| Borda / divisória | `#181E36` | contorno de 1 px, trilhas vazias |
| Acento roxo (vivo) | `#A58AFF` | nome "Alex", "AM", núcleo do anel do timer |
| Acento roxo (médio) | `#6F4BBA` | item ativo, botão play, dia selecionado |
| Roxo profundo | `#3C307E` | trilha do anel, fundo de badge, gradiente escuro |
| Violeta / magenta | `#B355E2` | ponta quente do gradiente do timer e do visualizador |
| Azul | `#3175D3` (vivo `#8AC3FF`) | reunião, badge Medium, ícone de matéria |
| Laranja / âmbar | `#E49F3D` (vivo `#FFDB72`) | almoço, sol do clima, Physics Quiz |
| Verde | `#5AA360` (vivo `#79CC7C`) | estudo na agenda, hábito cumprido |
| Vermelho | `#DE4F43` | semáforo da janela, alerta |
| Texto primário | `#EAEAF0` (branco `#FCFCFC` nos títulos) | valores e títulos |
| Texto secundário | `#72788A` | prazos, datas, rótulos |

Proporção: ~72 % da imagem é azul-quase-preto (`#00000C`–`#12182A`); o roxo ocupa ~2 % dos pixels e
responde por quase toda a saturação da tela. É esse desequilíbrio que faz o acento funcionar.

Gradiente do anel do timer e do visualizador: `#B355E2` → `#8A6BE0` → `#4E3C96`.

### O que daria pra aproveitar no painel

- Hora e data do cabeçalho no formato "display + rótulo pequeno" (hoje já é parecido).
- Visualizador de barras em gradiente em vez de cor chapada.
- Badge em pílula vazada para a linha de limites do Claude (verde/laranja/vermelho por faixa de uso).
- Grade de círculos cheio/vazado serve pro histórico diário das redes.

---

## Ref 02 — Folha de ícones e animações de loading (mono, dark)

Fonte: pinterest.com/pin/589197563750158432 (736×927,
`i.pinimg.com/736x/cd/da/33/cdda33e7ec9f17543151f838e3b5ff72.jpg`). Apareceu por acaso: foi o link
colado primeiro no lugar do da Ref 01. O título e a descrição do pin são anúncio de logo no Fiverr,
numa pasta "Logo Design Ideas" — repin com metadado sem relação com a imagem. Fica como referência
porque o conteúdo é útil por si só.

### Estrutura geral

- Folha de amostras, não interface: **7 linhas × 8 colunas = 56 quadros**, sobre painel cinza
  escuro centralizado com margem lateral preta.
- Cada quadro é um **quadrado arredondado** (~56 px, raio ~12 px) um tom mais claro que o painel,
  sem borda e sem sombra — o fundo do quadro é o que separa um do outro.
- Cada linha tem um **rótulo em versalete pequeno** (letterspacing largo, cinza médio) alinhado à
  esquerda, acima dos quadros.
- Monocromático: branco sobre cinza escuro, sem nenhuma cor de acento. Os meios-tons de cinza fazem
  o papel de opacidade/rastro nas animações.

### Linha a linha

| # | Linha | Informação | Como é apresentada |
|---|-------|------------|--------------------|
| 1 | CIRCLE | 8 quadros de um spinner circular | Arco branco de espessura média percorrendo o círculo; a cauda do arco esmaece em cinza — são os **frames de uma animação**, não 8 ícones diferentes |
| 2 | DOTS | 8 variações de agrupamento de pontos | Três pontos em linha, um ponto só, pirâmide de 4, pontos de tamanhos alternados, aglomerado orgânico, par — vocabulário de "carregando" por pontos |
| 3 | FADE CIRCLES | 8 quadros de um ponto que cresce e vira anel | Ponto pequeno → ponto grande → anel duplo; variação só de tamanho e preenchimento, mesma posição central |
| 4 | BALL | 8 quadros de bola quicando | Bolinha branca em alturas diferentes com **traço fino de sombra** embaixo que encurta conforme ela sobe; último quadro com duas bolas |
| 5 | TIME | 8 ícones de tempo | Relógio com ponteiro, relógio vazio, cronômetro, pêndulo/metrônomo, dois relógios de cuco, setor de pizza preenchido (progresso), ampulheta estilizada |
| 6 | WIFI | 8 quadros de sinal | Arcos do wifi em quantidade crescente (1, 2, 3 arcos), ponto só (sem sinal), antena vertical, antena com ondas dos dois lados — **frames de sinal conectando** |
| 7 | ICONS | 8 ícones utilitários | Lupa, envelope, fotos empilhadas, casa, download (seta + base), cápsula/bateria, caminhão de entrega, livro/mapa aberto — contorno fino branco, estilo uniforme |

### Padrões que valem copiar

- **Animação como série de frames num quadro fixo**: o elemento muda, a moldura não — o olho não
  precisa reacompanhar a posição.
- **Cauda em cinza** no spinner em vez de opacidade variável do mesmo branco: lê melhor em fundo
  escuro e é mais barato de desenhar em canvas.
- **Sombra como traço** (um risco fino que encurta) dá peso à bola sem gradiente nenhum.
- **Rótulo em versalete espaçado** separando blocos sem precisar de linha divisória nem card.
- Mostrar estado por **quantidade** (arcos do wifi, pontos) em vez de cor: funciona em painel
  monocromático e não compete com o acento usado em outro lugar.

### Paleta (valores estimados)

| Papel | Hex | Onde aparece |
|---|---|---|
| Fundo da folha | `#0D0D0D` | margens pretas laterais |
| Painel | `#161616` | retângulo que agrupa as linhas |
| Quadro | `#212121` | o quadrado arredondado de cada amostra |
| Traço primário | `#FFFFFF` | ícone e cabeça do spinner |
| Traço secundário | `#8A8A8A` | cauda do spinner, pontos esmaecidos |
| Traço terciário | `#4A4A4A` | sombra da bola, estado apagado |
| Rótulo | `#9A9A9A` | "CIRCLE", "DOTS", … |

Zero cor de acento — tudo resolvido em 4 tons de cinza mais branco.

### O que daria pra aproveitar no painel

- Spinner com cauda cinza no lugar de qualquer indicador de "carregando" do painel.
- Arcos crescentes como indicador de estado de conexão (OneDrive offline/sincronizando/ok).
- O vocabulário de ícone com contorno fino branco combina com o painel atual, que já é escuro e
  sem muita cor fora dos acentos.
