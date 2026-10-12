---
updated: 2026-10-12
tier: 2
---

# Mapa do projeto

<!-- TETO: 60 linhas FORA do bloco auto (o bloco é do script e não conta). O `git log` guarda o resto. -->

Painel em tela cheia (Python + HTML sem dependências de front) servido em `127.0.0.1:8787`,
mostrado num monitor virtual e transmitido pro tablet por Sunshine/Moonlight.

## Comandos

<!-- auto:start -->
gerado em: 2026-10-12

primeiro nível:

```
abrir-painel.sh
agenda.exemplo.json
agenda.py
AGENTS.md
atalhos.exemplo.json
CLAUDE.md
config.exemplo.json
docs
index.html
LICENSE
onedrive.py
README.md
redes.py
server.py
```
<!-- auto:end -->

| Ação | Comando |
|---|---|
| Build / teste / lint | não tem (Python puro + HTML); testar abrindo `http://127.0.0.1:8787` |
| Rodar | `systemctl --user restart toca-do-texugo.service` (depois de mexer nos `.py`) |
| Abrir o painel | `bash abrir-painel.sh` (sobe o serviço e abre o Chrome em modo app no monitor do `config.json`) |
| Ver log | `journalctl --user -u toca-do-texugo -f` |

Mexeu em `.py` → restart. Mexeu em `index.html` → nada: o painel recarrega sozinho (`/api/version`).

## Onde fica cada coisa

- `server.py` — HTTP + coleta. `Collector` amostra 1×/s numa thread; `GpuReader` (nvidia-smi),
  `RaplReader` (watts da CPU), `ClaudeUsage` (limites do Claude, linha 169), rotas no `Handler`
  (`do_GET` linha 403, `do_POST` linha 479).
- `index.html` — página inteira (HTML+CSS+JS). Cabeçalho linha 369, `render(s)` 747,
  `renderClaude` 863, `renderConfig` (tela de botões) 1147, **editor de grade** 1196, medidores do
  layout agrupado 1363, agenda 1617, `renderRedes` 1766; visualizador e texugo em canvas no fim.
- `redes.py` — uma classe por rede (`Youtube`, `Twitch`, `Kick`, `TikTok`; registro em `PROVIDERS`)
  + `Redes` que orquestra, guarda histórico diário e renova token sozinho.
- `agenda.py` — long polling do bot do Telegram; o "feito" é local do painel, nunca volta pro bot.
- `onedrive.py` — lê o journal do serviço `onedrive` e a cota (cache de 1 h).
- `abrir-painel.sh` — sobe o serviço e abre o Chrome em tela cheia; se a janela já existe, só
  reposiciona e dá o toggle de tela cheia (é o destravamento do congelamento por composição).
- `.githooks/pre-commit` — barra credencial/arquivo privado no commit (`git config core.hooksPath .githooks`).
- `docs/` — prints usados no README.

## Pontos de entrada e fluxos principais

- Painel: `GET /` → `index.html` → busca `/api/stats` 1×/s → `render(s)` desenha tudo.
- Métricas: thread do `Collector` → dict em `COLLECTOR.stats` → servido como JSON (nada é calculado por requisição).
- Redes: `redes.py` atualiza em segundo plano → `/api/redes` (o painel busca a cada 30 s).
- Áudio: `/api/audio` manda PCM s16le mono 24 kHz do monitor da saída padrão → FFT no navegador.
- Atalhos: `POST /api/run/<id>`, só ids de `~/.config/toca-do-texugo/atalhos.json`, exige `X-Dash: 1`.
- Agenda: bot do Telegram → `agenda.py` → `/api/agenda`; o toque no item faz `POST /api/agenda/<id>`.

## Arquivos locais (fora do repo, em `~/.config/toca-do-texugo/`)

`config.json` (máquina), `redes.json` (credenciais), `redes-tokens.json`, `redes-historico.json`,
`atalhos.json`, `agenda.json` (token do bot), `agenda-itens.json`, `onedrive-cota.json`,
`chrome/` (perfil do Chrome do painel).

## Arquivos de fora que apontam pra pasta do projeto

Mudou de pasta? Corrigir os três + `daemon-reload`: `systemd/user/toca-do-texugo.service`
(`ExecStart`), `autostart/toca-do-texugo.desktop` (login), `applications/…desktop` (menu).
