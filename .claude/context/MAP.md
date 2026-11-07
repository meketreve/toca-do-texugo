---
updated: 2026-10-16
tier: 2
---

# Mapa do projeto

<!-- TETO: 60 linhas FORA do bloco auto (o bloco é do script e não conta). O `git log` guarda o resto. -->

Painel em tela cheia (Python + HTML, sem build) em `127.0.0.1:8787`, num monitor virtual, no
tablet por Sunshine/Moonlight.

## Comandos

<!-- auto:start -->
gerado em: 2026-10-16

primeiro nível:

```
abrir-painel.sh
agenda.exemplo.json
agenda.py
atalhos.exemplo.json
atualizar-painel.sh
config.exemplo.json
docs
fontes
index.html
LICENSE
onedrive.py
README.md
redes.py
server.py
testes
texugo.py
```
<!-- auto:end -->

| Ação | Comando |
|---|---|
| Rodar / abrir | `systemctl --user restart toca-do-texugo.service` (só se mexeu em `.py`); `bash abrir-painel.sh` abre o Chrome |
| Ver log | `journalctl --user -u toca-do-texugo -f` |
| Testar sem o painel | `testes/README.md` (Chromium headless; `monta-telas.py --real` usa o dado da máquina) |
| Atualizar a máquina do painel | `bash atualizar-painel.sh` (puxa o `main`; `--voltar` desfaz) |

## Onde fica cada coisa

- `server.py` — HTTP + coleta (`Collector` 1×/s, `GpuReader`, `RaplReader`, `ClaudeUsage`), rotas no
  `Handler` e `_send_fonte` pra `/fontes/` (a única rota com cache).
- `index.html` — a página inteira: `render(s)` despacha pelo `PAGES[0]`, e o mascote fica no fim.
- **tema**: `<script>` do `<head>` aplica `painel.tema` (`data-tema` + `.g`/`.l`) antes do 1º
  desenho; no Grafite o clássico é `page-dash-g`, no Linha os dois layouts caem na grade.
- **barra lateral**: `#rail` no CSS base (coluna 1 do `.app`, 76 px); os temas só trocam a moldura.
- **telas**: atalhos lista `renderTelas()` (clássico + um botão por perfil) e `setTela()` grava o
  par; `renderEdPerfis()` é a barra do editor e `semeiaLinha()`/`ativaLinha()` criam as do Linha.
- perfis: `perfis()` lê `painel.perfis` `{nome: [itens]}`, `perfilAtual()` o ativo, e `layoutB()`/
  `salvarB()` falam só com o ativo.
- medidor: `medidor(id, nome, dadosDe, opts)` + `ESTILOS_MEDIDOR`; ele declara os itens UMA vez e
  todo estilo (inclusive os de `addEstilo`) lê os mesmos. `grupo` organiza o catálogo do editor.
- **Linha, peças**: `fontes/*.woff2` (Barlow Condensed, OFL) em `/fontes/`; `linhaCab()`, os
  estilos Encoders/Bancada/Faders/Faixa/Pratos/Cilindros e os medidores `relogio`/`musica` na seção
  "Tema Linha: os desenhos dos mockups". O Disco gira por `giraPratos()`, no quadro da animação.
- **configurações**: `page-config` (`cfrAbre`, `CFR`) ↔ `GET/POST /api/config/redes` ↔
  `redes.config_publica()`/`grava_config()` (o segredo nunca volta).
- `redes.py` (classe por rede + `Redes`), `agenda.py` (long polling do bot), `onedrive.py` (journal
  + cota) e `texugo.py` (spike + STDP: `Sensores`, `passo()`, `_vencedor()`).
- `abrir-painel.sh` (sobe o serviço e o Chrome; reposicionar + fullscreen é o que destrava o congelamento por composição), `atualizar-painel.sh` e `docs/` (prints).
- `testes/` (bancada em Chromium headless) e `.githooks/pre-commit` (barra credencial).

## Fluxos principais

- Painel: `GET /` → `index.html` → `/api/stats` 1×/s → `render(s)` (métricas: thread do `Collector`).
- Redes (`/api/redes`, 30 s), áudio (`/api/audio`, PCM mono 24 kHz → FFT), atalhos (`POST
  /api/run/<id>`, exige `X-Dash: 1`), agenda (bot → `/api/agenda`) e mascote (`/api/texugo` →
  `doCerebro()`; em `instinto`, `chooseNext()`).

## Fora do repo (`~/.config/toca-do-texugo/`)

`config.json`, `redes.json` (credenciais), `redes-tokens.json`, `redes-historico.json`,
`atalhos.json`, `agenda.json`, `agenda-itens.json`, `texugo-cerebro.json`, `onedrive-cota.json` e
`chrome/`. Mudou de pasta? Corrigir `systemd/user/…service`, `autostart/…desktop` e
`applications/…desktop` + `daemon-reload`.
