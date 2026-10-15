# 🦡 Toca do Texugo

Dashboard em tela cheia que roda num **monitor virtual** do Linux e é transmitido pro **tablet** com Sunshine + Moonlight. Mostra o hardware em tempo real, um visualizador que reage à música tocando, os números das redes sociais e tem um texugo em pixel art passeando por cima dos cards.

![Toca do Texugo rodando no monitor virtual](docs/painel.png)

## O que tem

**Monitoramento**
- CPU, RAM, GPU e VRAM com gráfico dos últimos 90 s (toque no gráfico pra ver o valor de cada segundo)
- Uso por thread da CPU, temperaturas (CPU, GPU, NVMe) e consumo em watts (RAPL + `nvidia-smi`)
- Discos, leitura e escrita, rede e os processos mais pesados (a lista se ajusta ao espaço)
- Volume, carga e uptime no cabeçalho

**Cérebro do texugo** (rede de spike com STDP)
- O mascote não tem uma tabela de "se acontecer X, faça Y": quem escolhe o comportamento é uma rede de neurônios com disparo e plasticidade sináptica, que aprende sozinha qual sinal do painel puxa qual reação
- 16 sensores (CPU, GPU, calor, rede, disco, música, hora do dia, picos e eventos) viram trens de spike; 6 neurônios de saída disputam o comando por inibição lateral
- Aprende o tempo todo, desde que o serviço sobe, e guarda o que aprendeu em disco — a personalidade se forma ao longo de dias
- Medidor **Cérebro** mostra os pesos se formando ao vivo, e a chave troca entre o cérebro e o instinto antigo

**OneDrive** (cliente [abraunegg/onedrive](https://github.com/abraunegg/onedrive))
- Estado da sincronização em tempo real (sincronizado há X, sincronizando, erro, sem conexão, serviço parado), lido do journal do serviço
- Cota da nuvem (`onedrive --display-quota`, 1× por hora), tamanho e número de arquivos da pasta local
- Últimos uploads, downloads e exclusões

**Música**
- **Tocando agora** pelo MPRIS (Spotify, navegador, VLC…): capa, título, artista e progresso
- **Visualizador de áudio** de 64 barras que capta o som do PC (qualquer programa), com FFT feita no navegador e ganho automático

![Tocando agora e visualizador de áudio](docs/musica.png)

**Redes sociais**
- Card na tela principal com seguidores, "+N hoje", views e likes de cada rede
- Página de detalhes com o último vídeo/post, os totais e a tendência dos últimos 30 dias
- Aviso **AO VIVO** no cabeçalho quando tem live na Twitch ou na Kick

| Rede | API | Dados |
|---|---|---|
| YouTube | Data API v3 (chave de API) | inscritos, views, likes somados, vídeos, último vídeo |
| Twitch | Helix (client credentials) | seguidores, live, espectadores, jogo |
| TikTok | Login Kit Desktop + Display API | seguidores, likes do perfil, views somadas, vídeos, último vídeo |
| Kick | endpoint interno `kick.com/api/v2` (sem credencial) | seguidores, live, espectadores, categoria |

**Limites do Claude** (só aparece pra quem usa o app de desktop)
- Quanto já foi usado da janela de **5 h** e da **semanal**, no cabeçalho, com o horário estimado do reset: `Claude 5 h 42%, reseta ~19h30 · semana 18%, reseta ~qui 09h`
- Amarelo passando de 75%, vermelho de 90%. Se a última amostra tiver mais de 45 min (app fechado), a linha fica cinza em vez de passar número velho por atual
- Sai do histórico que o próprio app de desktop grava em `~/.config/Claude/plan-usage-history.json`; o painel só **lê**, e só as porcentagens. Não tem API pública pra isso, então o formato pode mudar: se o arquivo sumir ou não der pra ler, a linha some junto
- O arquivo não guarda a hora do reset, só as porcentagens. Ela é estimada pelas viradas do histórico (a porcentagem cai, ou sai do zero), que é amostrado de 15 em 15 min — daí o `~`: o erro fica na casa dos 10 min. Se a virada caiu num buraco do histórico (app fechado na hora), o painel mostra a porcentagem e omite o horário

**Texugo** 🦡
- Anda por cima dos cards (menos a fileira de cima, pra não cobrir o cabeçalho) e pula de um pro outro, inclusive quando a página muda
- Dança no ritmo da música, dorme quando fica parado, sua quando o PC esquenta
- Comemora quando entra seguidor novo; tocar nele ganha um coração

**Páginas**: painel → redes → atalhos, trocadas por um botão discreto no canto inferior direito. A página de atalhos volta sozinha pro painel depois de 90 s sem toque.

## Como funciona

```
┌────────────── PC (Linux Mint) ──────────────┐           ┌── Tablet ──┐
│ server.py  :8787 ──► Chrome (modo app)      │           │            │
│   ├─ /api/stats   psutil, nvidia-smi, RAPL  │  monitor  │  Moonlight │
│   ├─ /api/audio   parec (monitor do som)    │  virtual  │            │
│   ├─ /api/redes   redes.py (APIs)           ├─ DP-0 ───►│            │
│   ├─ /api/texugo  texugo.py (rede de spike) │           │            │
│   └─ /api/version recarga automática        │ Sunshine  │            │
└─────────────────────────────────────────────┘           └────────────┘
```

- `server.py` coleta as métricas numa thread (1×/s), serve a página e só escuta em `127.0.0.1`
- `index.html` é a página inteira (HTML, CSS e JS, sem dependências): gráficos em SVG, visualizador e mascote em canvas
- `onedrive.py` acompanha o journal do serviço `onedrive` e lê a cota; nunca mexe no token do cliente
- `redes.py` busca os números das redes em segundo plano, guarda o histórico diário e renova os tokens sozinho
- `texugo.py` roda a rede de spike numa thread a 100 Hz e escolhe o comportamento do mascote
- `abrir-painel.sh` sobe o serviço e abre o Chrome em modo app, em tela cheia no `DP-0`
- O painel se recarrega sozinho quando o `index.html` muda

Pra mostrar a tela no tablet, usei o [**monitor-virtual-tablet**](https://github.com/meketreve/monitor-virtual-tablet): um monitor virtual na placa NVIDIA transmitido por uma segunda instância do Sunshine.

## Instalação

Precisa de Python 3 com `psutil`, `google-chrome`, `wmctrl`, `xrandr`, `curl`, `parec` (PulseAudio/PipeWire), `busctl` (systemd) e `nvidia-smi` pra GPU.

1. Serviço do usuário em `~/.config/systemd/user/toca-do-texugo.service`:

   ```ini
   [Unit]
   Description=Toca do Texugo (servidor local 127.0.0.1:8787)

   [Service]
   ExecStart=/usr/bin/python3 /caminho/para/toca-do-texugo/server.py
   KillMode=process
   Restart=on-failure
   RestartSec=3s
   ```

2. Pra abrir sozinho ao entrar na sessão, crie `~/.config/autostart/toca-do-texugo.desktop` com:

   ```ini
   [Desktop Entry]
   Type=Application
   Name=Toca do Texugo
   Exec=sh -c "sleep 15; bash /caminho/para/toca-do-texugo/abrir-painel.sh"
   X-GNOME-Autostart-enabled=true
   NoDisplay=true
   ```

3. Máquina: copie `config.exemplo.json` pra `~/.config/toca-do-texugo/config.json` e ajuste (tudo é opcional):

   | Chave | Pra que serve | Sem ela |
   |---|---|---|
   | `monitor` | saída do xrandr onde o painel abre | `DP-0` |
   | `rede` | interface de rede dos gráficos | a da rota padrão |
   | `discos` | lista de `{caminho, nome}` mostrados no card de discos | só `/` |
   | `cpu_tdp_w` | TDP da CPU pra barra de consumo | mostra só os watts |

4. Atalhos: copie `atalhos.exemplo.json` pra `~/.config/toca-do-texugo/atalhos.json` e ajuste. Cada item é `{id, label, icon, cmd}`, e só os ids desse arquivo podem ser executados.

Depois de mudar `server.py`, `redes.py` ou `onedrive.py`: `systemctl --user restart toca-do-texugo.service`.

## Configurando as redes

As credenciais ficam em `~/.config/toca-do-texugo/redes.json` (`chmod 600`, **fora do repo**). O arquivo é relido quando muda, sem precisar reiniciar:

```json
{
  "youtube":   { "handle": "@seu_canal", "api_key": "" },
  "twitch":    { "login": "seu_login", "client_id": "", "client_secret": "" },
  "kick":      { "usuario": "seu_slug" },
  "tiktok":    { "usuario": "seu_usuario", "client_key": "", "client_secret": "" }
}
```

- **YouTube**: no Google Cloud, ative a *YouTube Data API v3* e crie uma chave de API (de preferência restrita a essa API). Cada leitura gasta cerca de 5 unidades da cota diária de 10.000.
- **Twitch**: registre um app em dev.twitch.tv (tipo *Confidential*, redirect `http://localhost`) e copie o Client ID e um secret novo. Use um app próprio, pra não invalidar o secret de outros bots.
- **Kick**: só o slug do canal (o que vem depois de `kick.com/`), sem credencial. Os números saem do endpoint que o próprio site usa (`kick.com/api/v2/channels/<slug>`), que **não é documentado** e pode mudar ou passar a barrar. A API oficial (`api.kick.com`) exige app OAuth e mesmo assim não devolve número de seguidores, só a live — por isso a escolha. O Cloudflare do site recusa o `urllib`, então essa leitura vai por `curl`.
- **TikTok**: crie um app em developers.tiktok.com e um **Sandbox** com a sua conta como *target user*. Adicione o **Login Kit** com a plataforma **Desktop** e a Redirect URI `http://localhost:8787/tiktok/callback/`, e os escopos `user.info.basic`, `user.info.stats` e `video.list`. Depois abra `http://localhost:8787/tiktok/login` no navegador do PC e autorize. Os tokens se renovam sozinhos, e a autorização vale 1 ano.
  > **Pegadinha do portal:** se a aba **Web** do Login Kit guardar uma URI com `localhost`, o formulário recusa tudo, mesmo com a Web desmarcada. Coloque qualquer URL `https` nela.

Se a URI cadastrada no TikTok for outra, informe o endereço exato em `tiktok.redirect_uri` no `redes.json`.

## Agenda e recados pelo Telegram

Crie um bot com o [@BotFather](https://t.me/BotFather), mande qualquer mensagem pra ele e
descubra o seu `chat_id` em `https://api.telegram.org/bot<TOKEN>/getUpdates`. Copie o
`agenda.exemplo.json` pra `~/.config/toca-do-texugo/agenda.json` com os dois valores.

Daí é só mandar mensagem pro bot: o painel entende data e hora no começo do texto
("amanhã 14h dentista", "sexta comprar ração", "12/10 aniversário"). Mensagem sem data vira
recado solto. Tocar no item marca como feito.

O bot é público por natureza — qualquer um que descubra o nome dele consegue mandar mensagem.
Por isso tudo que não vier do `chat_id` configurado é descartado sem nem olhar o texto. O fluxo é
só de entrada: o painel lê as mensagens e nunca escreve de volta; "feito" é estado local.

## O cérebro do texugo

Inspirado no [DeskBuddy](https://www.tiktok.com/@jackyfernandess/video/7368840300162190597), de
[@jackyfernandess](https://www.tiktok.com/@jackyfernandess): em vez de um LLM, ou de uma regra
escrita à mão pra cada reação, o mascote é comandado por uma rede de neurônios com spike que
aprende por **STDP** (plasticidade dependente do tempo de disparo).

```
16 sensores do painel          6 comportamentos
  CPU, GPU, calor, memória  ┐   ┌ andar
  rede, disco, música       ├──►├ pular, parar
  volume, Claude, noite     │   ├ sentar, dormir
  picos e eventos           ┘   └ dançar
     (Poisson, 2 a 60 Hz)        (LIF, limiar adaptativo)
```

A cada passo de 10 ms:

| Mecanismo | O que faz |
|---|---|
| **STDP** | no instante do disparo, o sensor que estava ativo fortalece a sinapse; o que estava quieto, enfraquece |
| **Covariância** | cada sensor é comparado com a **própria média** — o que vive ligado (volume) fica neutro, e quem ensina é o "ligado agora, normalmente não" |
| **Inibição lateral** | quem dispara cala os outros por ~1,5 s e segue no comando enquanto a situação durar: é daí que sai a especialização |
| **Normalização** | a soma dos pesos que chegam num neurônio é constante, então os sensores competem entre si |
| **Homeostase** | o limiar sobe em quem dispara demais e desce em quem dispara de menos — nenhum comportamento morre nem domina pra sempre |

Não há recompensa nem supervisão: afagar o texugo **não** treina nada, de propósito. A escolha do
comportamento não é "quem disparou mais", e sim quem está disparando mais que o próprio normal
(desvio em unidades de ruído), pra neurônio barulhento não vencer em qualquer situação.

**Ligando:** o cérebro nasce desligado — adicione o medidor **Cérebro** pelo editor de grade e
toque em `cérebro`. Ele aprende desde o boot nos dois modos; o modo só decide quem comanda o
mascote. `instinto` volta pro comportamento sorteado de antes, e `esquecer` zera os pesos.

Pra ver a rede se organizando sem subir o painel (situações sintéticas, aprendizado acelerado):

```bash
python3 texugo.py 12 6
```

## Arquivos locais (nunca versionados)

| Arquivo | O que é |
|---|---|
| `~/.config/toca-do-texugo/config.json` | monitor, rede, discos e TDP da máquina |
| `~/.config/toca-do-texugo/redes.json` | credenciais das redes |
| `~/.config/toca-do-texugo/redes-tokens.json` | tokens renovados (TikTok) |
| `~/.config/toca-do-texugo/redes-historico.json` | histórico diário pro "+N hoje" e a tendência |
| `~/.config/toca-do-texugo/atalhos.json` | atalhos da página de atalhos |
| `~/.config/toca-do-texugo/agenda.json` | token do bot do Telegram e o seu `chat_id` |
| `~/.config/toca-do-texugo/agenda-itens.json` | itens da agenda e o offset já lido do Telegram |
| `~/.config/toca-do-texugo/texugo-cerebro.json` | pesos, limiares e idade do cérebro do texugo |
| `~/.config/toca-do-texugo/onedrive-cota.json` | última cota lida do OneDrive (cache de 1 h) |
| `~/.config/toca-do-texugo/chrome/` | perfil do Chrome do painel |

## Segurança

- O servidor só escuta em `127.0.0.1` e confere o cabeçalho `Host`. Os atalhos exigem o cabeçalho `X-Dash`, então outro site aberto no navegador não consegue disparar comandos.
- Os erros das APIs mostram só a mensagem, nunca a URL, que pode conter a chave.
- Do histórico do Claude o painel lê só as porcentagens e a hora da amostra. O identificador da organização, que está no mesmo arquivo, não é lido nem servido.
- O hook `.githooks/pre-commit` bloqueia commit com arquivo privado, formato de chave conhecido ou o **valor real** de alguma credencial local, sem imprimir o valor. Num clone novo, ative com:

  ```bash
  git config core.hooksPath .githooks
  ```

## API local

| Rota | Conteúdo |
|---|---|
| `GET /` | a página do painel |
| `GET /api/stats` | métricas do PC, música atual, status do OneDrive e limites do Claude (JSON, 1×/s) |
| `GET /api/audio` | PCM s16le mono 24 kHz do som do PC (stream) |
| `GET /api/redes` | números das redes, "+hoje" e histórico |
| `GET /api/agenda` | compromissos e recados vindos do Telegram |
| `GET /api/texugo` | estado do cérebro: comportamento, sensores, neurônios e pesos |
| `GET /api/shortcuts` | lista de atalhos (sem os comandos) |
| `POST /api/run/<id>` | executa um atalho (exige `X-Dash: 1`) |
| `POST /api/agenda/<id>/feito` | marca um item como feito (exige `X-Dash: 1`) |
| `POST /api/texugo/modo` | troca entre `cerebro` e `instinto` (exige `X-Dash: 1`) |
| `POST /api/texugo/esquecer` | zera o que o cérebro aprendeu (exige `X-Dash: 1`) |
| `GET /api/version` | data do `index.html`, pra recarga automática |
| `GET /tiktok/login` | inicia a autorização do TikTok |

## Licença

[MIT](LICENSE)
