---
updated: 2026-10-16
tier: 2
---

# Aprendizados

<!-- TETO: 100 linhas fora de blocos auto. Uma linha por fato, formato grepável: `- [AAAA-MM-DD] [tag] fato — consequência`.
     O que foi tentado ou decidido leva veredito depois da tag: [✓] testado e mantido, [✗] tentado e descartado (nunca apagar), [↻ AAAA-MM-DD] substituído pela entrada dessa data. -->

## Preferências do usuário

- [2026-09-28] [prefs] tudo em português; **comentários e docstrings no código sem acento** — README, textos da interface e mensagens de commit com acento normal
- [2026-09-28] [front] `index.html` é a página inteira, sem dependência externa e sem build — não introduzir framework nem CDN
- [2026-09-28] [privacidade] repo é público: antes de commitar, conferir que nada pessoal vaza — vale até pra exemplo de README (número inventado, não o valor real da máquina)
- [2026-09-28] [prefs] respostas curtas — sem repetir o código na conversa

## Pegadinhas (versão, API, CI)

- [2026-09-23] [claude-usage] `~/.config/Claude/plan-usage-history.json` não é formato público, pode mudar sem aviso — falha de leitura devolve `None` e o painel some com a linha
- [2026-09-23] [claude-usage] o arquivo é amostrado de **15 em 15 min** e só com o app de desktop aberto — o histórico tem buracos de horas quando o app fica fechado
- [2026-09-23] [privacidade] o mesmo arquivo tem o campo `org` (id da organização) — ler só `t` e `u`; nunca servir o `org`
- [2026-10-05] [onedrive] aviso "cURL/libcurl 8.5.0 has known HTTP/2 bugs" a cada start do servico e cosmetico: o proprio cliente liga `force_http_11` sozinho e nada quebra; o painel ignora (so `ERROR:` vira `_last_error`) -- nao e bug do projeto
- [2026-09-28] [deploy] mudou `.py` → `systemctl --user restart toca-do-texugo.service`; mudou `index.html` → não precisa, o painel recarrega sozinho
- [2026-10-16] [front] dá pra testar o `index.html` sem a máquina do painel: copiar a página, injetar um roteiro no fim, servir por `http.server` e rodar o Chromium com `--headless=new --dump-dom`, lendo o relatório de dentro do DOM. Duas pegadinhas: o editor escuta `pointerdown`, e `setPointerCapture` com `pointerId` sintético estoura `NotFoundError` e mata o resto do handler (no teste, virar no-op)
- [2026-09-28] [kick] `followers_count` vem como **string** e a hora da live em **UTC sem fuso** — os dois são convertidos no provider

## Erros a não repetir

- [2026-10-16] [front] `points` de `<polyline>` é lista de PARES de coordenadas, não `path`: com o "M" na frente a lista inteira é inválida, a polilinha fica sem geometria e **não desenha** — e nada avisa, porque a grade (feita de `<line>`) continua saindo. O traço do Uso ficou meses de fora assim que foi escrito; a bancada agora mede a altura do `getBBox()` das séries
- [2026-10-16] [medidores] classe curta dentro do desenho colide com a do número de fora: o knob do SVG usa `.vl` pro arco do valor e o número grande embaixo do desenho também é `.vl`, então o `querySelector(".vl")` do render achava o SVG primeiro e o número ficava em "—" pra sempre. Peças do desenho levam prefixo (`knob-vl`, `knob-pt`)
- [2026-10-16] [medidores] estrutura montada uma vez com os VALORES dentro: a legenda da bancada só era escrita quando mudava a quantidade de itens, então mostrava o número do primeiro render pra sempre. Montar a casca uma vez e reescrever os valores a cada passo (`leg.children[i].querySelector(".vl")`)
- [2026-10-16] [front] despachar o desenho pelo **`layout`** (o que o dono escolheu) e não pela **PÁGINA** na tela: no tema Linha o clássico cai na grade (`paginaDe`), então o `render()` chamava o desenho da página clássica e a grade ficava montada e **sem desenho** — rótulo e cartão vazio, sem erro nenhum (o `renderDashB` nem era chamado). `render()` agora pergunta por `PAGES[0]`. Nem o relatório de erro nem os prints com `layout=agrupado` pegavam: o caso é a COMBINAÇÃO tema + layout, não o tema
- [2026-10-16] [testes] teste que só olha erro de JS não vê cartão vazio: `renderDashB` engole a exceção de um medidor, e medidor que nunca foi desenhado não gera erro. O `monta-telas.py` reporta quanto cada cartão desenhou (`r.desenho`, o tamanho do `#widgets-b .widget .w-body`), que é o que pega esse caso
- [2026-10-16] [front] `grid-row: 2` com `grid-template-rows` de UMA linha cai numa linha IMPLICITA: no Linha (que esconde o cabeçalho e por isso tem uma linha só) o `main` foi pra uma linha `auto` fora do template e a grade do painel desabou de 6 pra 3 linhas — o `calcLinhas()` mede a altura que sobrou. Quando o tema mexe no template, ele tem que dizer onde o `main` fica
- [2026-10-16] [medidores] `addEstilo` entregava os stats CRUS em vez dos itens do medidor: todo estilo acrescentado depois do registro desenhava vazio (ou remontava a lista por conta própria e divergia calado). Agora `medidor()` guarda o `dadosDe` no widget e `addEstilo` embrulha com o mesmo `comDados()` — o estilo novo lê os MESMOS itens, com `curto`/`rodape`/`tag` — consequência: estilo novo não adivinha formato nem duplica lista
- [2026-10-16] [testes] o `--screenshot` do Chrome redimensiona a PÁGINA pro tamanho do print e o `--dump-dom` não: o mesmo teste mede cartões de 510 px no relatório e 548 px no print, e parece bug de grade que não existe — print com `--window-size=1920,1080`, relatório com `1920,1167` (o Chrome desconta ~87 px de janela)
- [2026-10-16] [testes] layout medido antes da fonte carregar não vale: o roteiro do `monta-telas.py` espera 5,2 s de tempo virtual de propósito, senão mede o layout da fonte de reserva

- [2026-10-16] [testes] print headless do clássico mostra "Uso por thread" por cima de "Temperaturas" — é métrica de fonte do Chrome headless, a versão antiga sai igual; na parede está certo. Pra print com tema/perfil: servir o `index.html` com `localStorage` injetado e repassar `/api` pro 8787
- [2026-10-16] [shell] `pkill -f "<trecho>"` mata o próprio shell quando o trecho aparece na linha de comando — ancorar: `pkill -f "^python3 …"`

- [2026-10-16] [front] o painel recarrega SOZINHO a cada save do `index.html`: um parêntese errado foi direto pra parede e, como o poll do `/api/version` morria junto, ela travou até reabrir o Chrome. O poll agora mora num `<script>` próprio; mesmo assim, conferir antes de salvar — extrair os `<script>` e `node --check`
- [2026-10-16] [editor] células do canvas no fluxo automático da grade: o bloco empurrava as que cobre pra linhas extras e o canvas parecia ter o dobro das linhas — célula com `grid-area` fixo, e linha com a proporção da célula do painel (`edMedeCanvas`)

- [2026-10-16] [texugo-snn] sensor `noite` nasceu com o sinal trocado (`0.5 - 0.5·cos` → pico às 15 h) e ninguém viu porque na matriz "noite aceso" parece normal — sensor novo de relógio: conferir o valor numa hora conhecida no `/api/texugo`

- [2026-10-16] [front] migração de formato NÃO pode normalizar na hora de gravar: o `normaliza()` corta altura e y pelo `LINHAS`, que depende do tamanho da janela NAQUELE instante — gravar o resultado cravaria uma tela pequena pra sempre. A migração dos perfis guarda o valor antigo como está e normaliza só na leitura
- [2026-10-16] [front] `.cb-corpo` É a grade da matriz do Cérebro (2 colunas): estilo novo que põe um filho só cai dentro da 1ª coluna e desenha espremido — ou pede `grid-column: 1 / -1` (Perfis) ou vira bloco (Rede). Dois estilos caíram nisso
- [2026-10-16] [texugo-snn] a inibição lateral vive perto do teto: medido em 120 amostras, 86% dos neurônios ficam acima de 0,3 o tempo todo, então corte fixo marca todo mundo. O que informa é o RELATIVO — o espalhamento entre eles é 0,68 na mediana, e o vencedor é o menos inibido em 70% das amostras
- [2026-10-15] [front] menu flutuante dentro de container com rolagem: comparar com `scrollHeight` (conteúdo todo) deixa o menu de um bloco da última linha abrir cortado — a conta é com a parte VISÍVEL, `scrollTop + clientHeight`
- [2026-10-15] [medidores] estilo alternativo que remonta a própria lista de dados DIVERGE calado: a temperatura do NVMe virou "SSD NVMe" num estilo e "NVMe" no outro. Medidor declara os itens uma vez (`medidor()`), estilo só desenha
- [2026-10-15] [front] `const` em zona morta temporal derruba o script inteiro: `ESTILOS_MEDIDOR` declarado depois das chamadas `gaugeWidget(...)` dava `Cannot access before initialization` e a página virava relógio `--:--`. Primitivas antes dos medidores no arquivo
- [2026-10-15] [front] o editor escuta `pointerdown`, não `click` — `.click()` sintético em teste não dispara nada e parece bug que não existe
- [2026-10-15] [front] `montados` é um Map por id do medidor: o mesmo medidor duas vezes na grade deixa o primeiro card vazio (o catálogo já desabilita o repetido, mas um layout montado na mão esbarra nisso)
- [2026-10-15] [texugo-snn] inibição lateral divisiva ACUMULA: sem teto < 1 os perdedores chegam a 1.0, que é surdez permanente (carga × 0) e nunca mais disparam nem com limiar no piso — `INIB_MAX = 0.8`
- [2026-10-15] [texugo-snn] limiar grudado no teto = homeostase desligada: o neurônio dispara acima do alvo e vence o voto em qualquer situação. Teto é salvaguarda (60), não faixa de operação
- [2026-10-15] [texugo-snn] escala de tempo é tudo: o domínio do vencedor tem que durar na ordem do comportamento (~1,5 s), a homeostase mais lenta que ele, e a janela do voto com spike suficiente pra z significar algo (5 s a 4 Hz ≈ 20) — errando isso a rede funciona e não aprende nada
- [2026-10-15] [front] widget que refaz `innerHTML` a cada segundo faz o alvo do toque sumir debaixo do dedo e repinta o card no vídeo do Moonlight — montar a estrutura uma vez e só trocar estilo (ver medidor Cérebro)
- [2026-10-15] [front] comportamento do mascote com prazo longo (dormir até 90 s) engole as reações seguintes: o cérebro precisa poder PREEMPTAR o comportamento vigente, com piso de 2 s contra tremelique
- [2026-10-12] [mudanca-de-pasta] o repo não tem caminho absoluto, mas 3 arquivos FORA dele apontam pra pasta do projeto: `~/.config/systemd/user/toca-do-texugo.service` (`ExecStart`), `~/.config/autostart/toca-do-texugo.desktop` (login) e `~/.local/share/applications/toca-do-texugo.desktop` (menu) — mudou de pasta, corrigir os três + `daemon-reload`; na mudança de 2026-10-11 o do menu passou batido e ficou quebrado
- [2026-10-12] [mudanca-de-pasta] `core.hooksPath .githooks` é por clone e **não** viaja na cópia — depois de mover/clonar, reconfigurar, senão o `pre-commit` que barra credencial em repo público não roda
- [2026-10-12] [chrome] painel "travado" também pode ser a janela do Chrome morta (o serviço segue 200): confere com `wmctrl -lx | awk '$3 ~ /toca-do-texugo$/'` e resolve com `bash abrir-painel.sh`, que reabre ou só reposiciona se já existir — cuidado que o jogo El Texugo da Steam também casa com "texugo" na busca por título
- [2026-10-01] [chrome] painel "travado" nem sempre é a página: se o servidor segue recebendo requisição, parou a composição do Chrome — destrava com o toggle de tela cheia do `wmctrl` (diagnóstico em `BUGS.md`)
- [2026-09-28] [css] `.live` (AO VIVO no cabeçalho) é `inline-flex`: texto quebrado em vários elementos perde os espaços — montar a frase num elemento só e trocar o `innerHTML`
- [2026-09-28] [rede] não servir na rede: o servidor só escuta em `127.0.0.1` e confere o `Host` — o tablet vê o painel pelo vídeo do Sunshine, não por HTTP

- [2026-10-16] [mascote] plataforma que não cabe não é plataforma: o texugo em pé ocupa `MH` ACIMA das patas (o pé fica na borda de cima do cartão), então no tema Linha — que não tem cabeçalho e por isso tem a fileira de cima colada no alto — ele subia metade pra fora da tela. `platforms()` agora pede `rect.top >= MH + 4`; no Atual e no Grafite nada muda (a fileira de cima já começa abaixo do cabeçalho)

## Decisões e o porquê

- [2026-10-16] [front] [✓] "Tela do painel" no lugar de "Layout do painel" + "Perfil de medidores": eram dois seletores que se atropelavam — o layout escolhe a PÁGINA (o clássico é uma página fixa, escrita à mão; o agrupado é a grade) e o perfil escolhe QUAIS medidores na grade, ou seja, o perfil não faz nada no clássico. A lista agora é de telas: "Clássico" + uma por perfil. Seguem sendo dois estados por baixo (`painel.layout` e `painel.perfil`), porque o clássico NÃO cabe num perfil: as peças dele (tela, tiles, processos, disco) não são medidores do registro — virá-los medidores mudaria o Atual, que é a referência de "não mexer"
- [2026-10-16] [medidores] [✓] giro do carretel em JS, no `requestAnimationFrame` que já roda (mascote/viz), e não com `animation-duration`: duração trocada de 1 em 1 s dá um degrau (o disco salta de lento pra rápido), enquanto a velocidade que PERCORRE até a nova acelera e freia como um carretel de verdade, e para sozinha quando a vazão zera. O vinil do card Tocando agora continua em CSS, que é giro constante
- [2026-10-16] [front] [✓] barra lateral em TODOS os temas, e o botão discreto de trocar página (`#pager`) fora: eram duas navegações pra mesma coisa, e a que se vê ganha. Ela é a coluna 1 da grade do `.app` (76 px) e o Grafite/Linha só trocam a moldura (raio, cor do item ativo) — o miolo (logo, botões de 48 px, ponto de conexão) é o mesmo. Com a barra em todo lugar, o aviso "volta ao painel em N s" da página de atalhos também aparece nos três temas: a volta sempre aconteceu em todos, só era invisível no Atual
- [2026-10-16] [tema] [✓] perfil de tema liga o tema: escolher "Linha · Dados" no seletor de perfil com o Atual ou o Grafite ligado mostrava os cartões na fonte e nas cores do outro tema — a tela e o tema andam em par, nos dois sentidos (`setPerfil` → `setTema`, e `setTema("linha")` → tela da máquina)
- [2026-10-16] [tema] [✓] Linha entra como OPÇÃO, mesmo contrato do Grafite: cores em `data-tema="linha"`, estrutura sob `.l`, Atual intacto. As duas telas do mockup ("mostradores da máquina" e "dados, música e texugo") são PERFIS de medidores de 4×3 — a grade já é 12×6 e o perfil já tem seletor e editor —, semeados por `semeiaLinha()` na primeira vez que o tema liga e sem apagar perfil nenhum
- [2026-10-16] [medidores] [✓] o LAYOUT do desenho é do medidor, não do tema: `.len`, `.lbn`, `.lfd`, `.lpf`, `.lpr`, `.lcl`, `.lrl`, `.lms` e a tipografia dos números ficam fora do `.l` — o tema só põe a cara (cartão, rótulo, canto, cores). Sem isso, escolher um perfil do Linha em outro tema dava cartão vazio, porque o CSS que dá tamanho ao SVG não existia ali
- [2026-10-16] [tema] [✓] no Linha o cabeçalho sai e o que ele mostrava vira o card Relógio: é o que faz o `calcLinhas()` fechar em 6 e a grade ficar 3×2 igual ao mockup. O AO VIVO e o ponto de conexão sobem pro canto do rótulo desse card (a barra lateral está escondida no Linha, então o ponto sumiria). E o layout clássico também cai na grade (`paginaDe`), senão quem está em "Clássico" veria a página do Atual com as cores do Linha
- [2026-10-16] [medidores] [✓] `curto`, `rodape` e `tag` no item do medidor: os mockups pedem número grande com unidade/limite pequenos e rótulo curto ("W", "°C") no mostrador, e o estilo não pode remontar a lista pra isso — o item é declarado UMA vez e o estilo só escolhe o que usar
- [2026-10-16] [fonte] [✓] Barlow Condensed vendorizada em `fontes/` (3 pesos × latin/latin-ext) e servida em `/fontes/<arquivo>` pelo próprio `server.py`, em vez de Google Fonts: o painel não pode depender de internet no boot e a regra da casa é não ter dependência externa. O `@font-face` fica declarado sempre, mas o navegador só baixa o arquivo quando algum elemento usa a família — no Atual e no Grafite nada usa
- [2026-10-16] [config] [✓] página de configurações nunca recebe segredo de volta (só `definido`), e Client ID/key contam como segredo — a tela vai pelo Sunshine e pode estar na live. Segredo vazio = mantém; `null` = apaga

- [2026-10-16] [tema] [✓] Grafite é OPÇÃO (`painel.tema`), não substituto: cores em `data-tema`, estrutura só sob `.g` — o Atual fica byte a byte igual. Trocar de tema recarrega a página (cores do canvas lidas uma vez, página do layout muda)
- [2026-10-16] [tema] [✓] no Grafite o clássico vira outra página (`page-dash-g`), não CSS por cima da antiga: o mockup junta 4 cards num só com abas e muda Redes de lugar — CSS não remonta isso

- [2026-10-16] [texugo-snn] [✓] o perfil do Cérebro lê o peso MENOS a média da coluna (o mesmo sensor nos outros comportamentos), com piso 0,20 — peso cru faz todo comportamento "preferir" o sensor que se correlaciona com tudo, e sem piso um cérebro de 0 spike já exibe gosto por sorteio (medido: em 500 nascimentos o desvio máximo foi 0,186; gosto aprendido fica entre 0,24 e 0,53)
- [2026-10-15] [texugo-snn] [✓] cérebro no Python (`texugo.py`, thread a 100 Hz), não no `index.html` — STDP precisa de passo de ~10 ms pra janela temporal significar algo (a 1×/s do Collector tudo seria simultâneo) e no servidor os pesos sobrevivem a recarregar a página
- [2026-10-15] [texugo-snn] [✓] entrada são os sinais do painel, não pixel da tela — na máquina o monitor do painel só mostra o painel, então capturar a tela seria circular; os stats já dão 16 canais prontos
- [2026-10-15] [texugo-snn] [✓] sem recompensa: afagar o texugo não treina (STDP puro + homeostase) — a homeostase é que garante que nenhum comportamento morra, que era a preocupação; a personalidade sai sem supervisão
- [2026-10-15] [texugo-snn] [✓] modo nasce em `instinto` — a chave mora no medidor Cérebro, que não está no layout padrão; vir ligado trocaria o comportamento sem o dono ter onde desligar. Aprende nos dois modos
- [2026-10-15] [texugo-snn] [✗] STDP em par pré/pós com depressão a cada spike de entrada — a depressão fica proporcional à TAXA do sensor, não à correlação: cpu/gpu/rede/musica foram a zero e a rede morreu de fome. Virou STDP só no pós-spike (Diehl & Cook)
- [2026-10-15] [texugo-snn] [✗] limiar fixo separando potenciar de deprimir — sensor sempre ligado domina todos os neurônios e sensor que marca uma situação morre antes de especializar alguém. Virou covariância: cada sensor contra a própria média
- [2026-10-15] [texugo-snn] [✗] voto por contagem bruta de spike, e também `votos/max(taxa,piso)` — o primeiro faz o neurônio mais barulhento vencer sempre, o segundo faz um spike solto de neurônio quieto valer mais que empolgação real. Virou z de Poisson `(votos-esperado)/√(esperado+1)`
- [2026-09-28] [kick] [✓] endpoint interno `kick.com/api/v2/channels/<slug>` (sem credencial) — a API oficial exige app OAuth e **não** devolve seguidores, que é o número do card; card conferido com número real em 2026-10-03
- [2026-09-28] [kick] [✗] ler o `kick.com` com `urllib` — o Cloudflare devolve 403; a leitura vai por `curl`
- [2026-09-28] [redes] [✗] Instagram no card de redes — saiu, trocado pela Kick (exigia conta Profissional e token de 60 dias)
- [2026-09-23] [claude-usage] [✓] limites do Claude como **linha no cabeçalho**, não card — o card ia tomar o lugar do painel de redes sociais
- [2026-09-23] [claude-usage] [✓] hora do reset **estimada** pelas viradas do histórico (porcentagem cai ou sai do zero; meio entre as duas amostras + duração da janela) — validado contra 30 dias: 10 de 10 previsões certas, erro mediano 10 min; daí o `~`, arredondar de 5 em 5 min e não mostrar horário quando a virada cai num buraco > 1 h
- [2026-09-19] [chrome] [✓] flags `--disable-backgrounding-occluded-windows` e cia. no `abrir-painel.sh` (0219986) — evitam o throttling por janela oculta, mas não cobrem a parada de composição de 2026-10-01
