---
updated: 2026-10-16
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
| Testar sem o painel | `testes/README.md` (Chromium headless) |
| Ver log | `journalctl --user -u toca-do-texugo -f` |
| Atualizar a máquina do painel | `bash atualizar-painel.sh` (puxa o `main`; `--voltar` desfaz) |

Mexeu em `.py` → restart. Mexeu em `index.html` → nada: recarrega sozinho (`/api/version`).
## Onde fica cada coisa

- `server.py` — HTTP + coleta: `Collector` 1×/s, `GpuReader`, `RaplReader`, `ClaudeUsage` (l. 169),
  rotas no `Handler` (`do_GET` l. 403, `do_POST` l. 479).
- **tema**: `<script>` no `<head>` aplica `painel.tema` (`data-tema` + classe `.g`/`.l`) antes do 1º
  desenho; CSS do Grafite e do Linha no fim do `<style>`; `TEMAS`/`paginaDe()` no JS — no Grafite o
  clássico é `page-dash-g`, no Linha os dois layouts caem na grade e as telas do mockup são PERFIS
  (`semeiaLinha()`/`ativaLinha()`, antes de `/* Paginas */`). Trocar tema = `location.reload()`.
- **Linha, peças**: `fontes/*.woff2` (Barlow Condensed, OFL) na rota `/fontes/<arquivo>`
  (`Handler._send_fonte`, a única com cache); `linhaCab()`, `comDados()`/`addEstilo()` e os estilos
  Encoders/Bancada/Faders/Faixa/Pratos/Cilindros + os medidores `relogio` e `musica` na seção "Tema
  Linha: os desenhos dos mockups", depois do medidor `capacidade`.
- **configurações**: `page-config` (`cfrAbre`, `CFR` no `index.html`) ↔ `GET/POST /api/config/redes`
  ↔ `redes.config_publica()`/`grava_config()` (`CAMPOS` diz o que é segredo; segredo nunca volta).
- `index.html` — página inteira. Cabeçalho 418, `render(s)` 796, `renderClaude` 912, `renderConfig`
  1216, **editor de grade** 1265, medidores 1499, cérebro 1853 (estilo Matriz 1922, Perfis 1969),
  agenda 2010, `renderRedes` 2142; mascote no fim (`chooseNext`/`doCerebro` escolhem o jeito).
- perfis de medidores: `perfis()` l. 1165 lê `painel.perfis` `{nome: [itens]}`, `perfilAtual()` o
  ativo (`painel.perfil`), `layoutB()`/`salvarB()` l. 1188 falam só com o perfil ativo, seletor em
  `renderPerfis()` l. 1289. NÃO confundir com `painel.layout`, que é clássico vs agrupado.
- camada de medidor: `medidor(id, nome, dadosDe, opts)` + `ESTILOS_MEDIDOR` (anéis/barras/números);
  o medidor declara os itens UMA vez e os estilos leem os mesmos. Cada um diz seu `grupo`
  (`GRUPOS`, l. 1052), que é por onde o catálogo do editor se organiza — sem grupo cai em "Outros".
- `redes.py` — uma classe por rede (`PROVIDERS`) + `Redes`: histórico diário e token renovado só.
- `agenda.py` — long polling do bot do Telegram; o "feito" é local do painel, nunca volta pro bot.
- `texugo.py` — cérebro do mascote (spike + STDP, 100 Hz): `Sensores`, `passo()`, `_vencedor()`
  (z de Poisson), e `_publica` manda sensores, neurônios (carga, voto, `inib`, z) e pesos.
  Teste solto: `python3 texugo.py 12 6`.
- `onedrive.py` — lê o journal do serviço `onedrive` e a cota (cache de 1 h).
- `abrir-painel.sh` — sobe o serviço e abre o Chrome em tela cheia; se a janela já existe, só
  reposiciona e dá o toggle (destrava o congelamento por composição). `docs/` — prints do README.
- `atualizar-painel.sh` — `fetch` + `merge --ff-only` do `main`, restart só se mudou `.py`, e
  `reset --hard` de volta se o painel não responder depois. Sha anterior em
  `~/.config/toca-do-texugo/atualizar-anterior`.
- `testes/` — bancada: Chromium headless contra uma cópia do `index.html` com roteiro
  injetado, e o `atualizar-painel.sh` contra remoto falso. Leia o `testes/README.md`.
- `.githooks/pre-commit` — barra credencial no commit (`git config core.hooksPath .githooks`).

## Pontos de entrada e fluxos principais

- Painel: `GET /` → `index.html` → busca `/api/stats` 1×/s → `render(s)` desenha tudo.
- Métricas: thread do `Collector` → `COLLECTOR.stats` → JSON (nada calculado por requisição).
- Redes: `redes.py` em segundo plano → `/api/redes` (o painel busca a cada 30 s).
- Áudio: `/api/audio` manda PCM s16le mono 24 kHz do monitor da saída padrão → FFT no navegador.
- Atalhos: `POST /api/run/<id>`, só ids de `~/.config/toca-do-texugo/atalhos.json`, exige `X-Dash: 1`.
- Agenda: bot do Telegram → `agenda.py` → `/api/agenda`; o toque no item faz `POST /api/agenda/<id>`.
- Mascote: `texugo.py` → `/api/texugo` (1×/s) → `doCerebro()`; em `instinto`, `chooseNext()`.

## Arquivos locais (fora do repo, em `~/.config/toca-do-texugo/`)

`config.json`, `redes.json` (credenciais), `redes-tokens.json`, `redes-historico.json`,
`atalhos.json`, `agenda.json` (bot), `agenda-itens.json`, `texugo-cerebro.json`,
`onedrive-cota.json`, `chrome/` (perfil do painel).

## Arquivos de fora que apontam pra pasta do projeto
Mudou de pasta? Corrigir os três + `daemon-reload`: `systemd/user/toca-do-texugo.service`
(`ExecStart`), `autostart/toca-do-texugo.desktop` (login), `applications/…desktop` (menu).
