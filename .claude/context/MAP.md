---
updated: 2026-10-03
tier: 2
---

# Mapa do projeto

<!-- TETO: 60 linhas FORA do bloco auto (o bloco é do script e não conta). O `git log` guarda o resto. -->

Painel em tela cheia (Python + HTML sem dependências de front) servido em `127.0.0.1:8787`,
mostrado num monitor virtual e transmitido pro tablet por Sunshine/Moonlight.

## Comandos

<!-- auto:start -->
gerado em: 2026-10-03

primeiro nível:

```
abrir-painel.sh
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

`index.html` não precisa de restart: o painel se recarrega sozinho quando o arquivo muda (`/api/version`).

## Onde fica cada coisa

- `server.py` — HTTP + coleta. `Collector` amostra 1×/s numa thread; `GpuReader` (nvidia-smi),
  `RaplReader` (watts da CPU), `ClaudeUsage` (limites do Claude, ~linha 168), rotas no `Handler`
  (`do_GET` ~linha 400, `do_POST` ~linha 475).
- `index.html` — página inteira (HTML+CSS+JS). Cabeçalho ~linha 222, `render(s)` ~linha 465,
  `renderClaude` ~573, `renderRedes` ~785; visualizador e texugo em canvas no fim do arquivo.
- `redes.py` — uma classe por rede (`Youtube`, `Twitch`, `Kick`, `TikTok`; registro em `PROVIDERS`)
  + `Redes` que orquestra, guarda histórico diário e renova token sozinho.
- `onedrive.py` — lê o journal do serviço `onedrive` e a cota (cache de 1 h).
- `abrir-painel.sh` — flags do Chrome contra congelamento e posicionamento via `wmctrl`.
- `.githooks/pre-commit` — barra credencial/arquivo privado no commit (`git config core.hooksPath .githooks`).
- `docs/` — prints usados no README.

## Pontos de entrada e fluxos principais

- Painel: `GET /` → `index.html` → busca `/api/stats` 1×/s → `render(s)` desenha tudo.
- Métricas: thread do `Collector` → dict em `COLLECTOR.stats` → servido como JSON (nada é calculado por requisição).
- Redes: `redes.py` atualiza em segundo plano → `/api/redes` (o painel busca a cada 30 s).
- Áudio: `/api/audio` manda PCM s16le mono 24 kHz do monitor da saída padrão → FFT no navegador.
- Atalhos: `POST /api/run/<id>`, só ids de `~/.config/toca-do-texugo/atalhos.json`, exige `X-Dash: 1`.

## Arquivos locais (fora do repo, em `~/.config/toca-do-texugo/`)

`config.json` (máquina), `redes.json` (credenciais), `redes-tokens.json`, `redes-historico.json`,
`atalhos.json`, `onedrive-cota.json`, `chrome/` (perfil do Chrome do painel).
