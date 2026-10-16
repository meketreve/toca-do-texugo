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

## Decisões e o porquê

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
