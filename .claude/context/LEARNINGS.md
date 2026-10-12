---
updated: 2026-10-12
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
- [2026-09-28] [kick] `followers_count` vem como **string** e a hora da live em **UTC sem fuso** — os dois são convertidos no provider

## Erros a não repetir

- [2026-10-12] [mudanca-de-pasta] o repo não tem caminho absoluto, mas 3 arquivos FORA dele apontam pra pasta do projeto: `~/.config/systemd/user/toca-do-texugo.service` (`ExecStart`), `~/.config/autostart/toca-do-texugo.desktop` (login) e `~/.local/share/applications/toca-do-texugo.desktop` (menu) — mudou de pasta, corrigir os três + `daemon-reload`; na mudança de 2026-10-11 o do menu passou batido e ficou quebrado
- [2026-10-12] [mudanca-de-pasta] `core.hooksPath .githooks` é por clone e **não** viaja na cópia — depois de mover/clonar, reconfigurar, senão o `pre-commit` que barra credencial em repo público não roda
- [2026-10-12] [chrome] painel "travado" também pode ser a janela do Chrome morta (o serviço segue 200): confere com `wmctrl -lx | awk '$3 ~ /toca-do-texugo$/'` e resolve com `bash abrir-painel.sh`, que reabre ou só reposiciona se já existir — cuidado que o jogo El Texugo da Steam também casa com "texugo" na busca por título
- [2026-10-01] [chrome] painel "travado" nem sempre é a página: se o servidor segue recebendo requisição, parou a composição do Chrome — destrava com o toggle de tela cheia do `wmctrl` (diagnóstico em `BUGS.md`)
- [2026-09-28] [css] `.live` (AO VIVO no cabeçalho) é `inline-flex`: texto quebrado em vários elementos perde os espaços — montar a frase num elemento só e trocar o `innerHTML`
- [2026-09-28] [rede] não servir na rede: o servidor só escuta em `127.0.0.1` e confere o `Host` — o tablet vê o painel pelo vídeo do Sunshine, não por HTTP

## Decisões e o porquê

- [2026-09-28] [kick] [✓] endpoint interno `kick.com/api/v2/channels/<slug>` (sem credencial) — a API oficial exige app OAuth e **não** devolve seguidores, que é o número do card; card conferido com número real em 2026-10-03
- [2026-09-28] [kick] [✗] ler o `kick.com` com `urllib` — o Cloudflare devolve 403; a leitura vai por `curl`
- [2026-09-28] [redes] [✗] Instagram no card de redes — saiu, trocado pela Kick (exigia conta Profissional e token de 60 dias)
- [2026-09-23] [claude-usage] [✓] limites do Claude como **linha no cabeçalho**, não card — o card ia tomar o lugar do painel de redes sociais
- [2026-09-23] [claude-usage] [✓] hora do reset **estimada** pelas viradas do histórico (porcentagem cai ou sai do zero; meio entre as duas amostras + duração da janela) — validado contra 30 dias: 10 de 10 previsões certas, erro mediano 10 min; daí o `~`, arredondar de 5 em 5 min e não mostrar horário quando a virada cai num buraco > 1 h
- [2026-09-19] [chrome] [✓] flags `--disable-backgrounding-occluded-windows` e cia. no `abrir-painel.sh` (0219986) — evitam o throttling por janela oculta, mas não cobrem a parada de composição de 2026-10-01
