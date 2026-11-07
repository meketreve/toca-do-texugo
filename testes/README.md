# Bancada

O painel precisa da máquina dele (serviço, `/api/stats`, monitor DP-0) pra rodar de verdade, mas
o `index.html` dá pra exercitar em qualquer lugar: copia da página com um roteiro injetado no fim,
servida por `http.server`, aberta no Chromium em `--headless=new --dump-dom`. O roteiro escreve um
relatório JSON dentro do próprio DOM e o `--dump-dom` traz ele de volta.

Nada disso roda no painel nem entra na página servida: é tudo cópia, em `testes/_saida/`
(ignorada pelo git).

| Arquivo | O que faz |
|---|---|
| `monta.py` | catálogo do editor: grupos, abrir/fechar, pôr medidor, "sem espaço" |
| `monta-cerebro.py` | os três estilos do medidor Cérebro, com dado real do `texugo.py` |
| `monta-perfis.py` | telas (clássico + perfis) em DUAS páginas, pra testar o reload de verdade |
| `monta-telas.py` | as telas com um `/api` falso: as duas do tema Linha, o clássico, o agrupado e o Grafite (pra comparar print com mockup e pegar regressão nos temas que não mudaram), mais quatro testes de ponta a ponta — trocar o tema, escolher um perfil pelo seletor e navegar pela barra lateral (`teste-atalhos*`) |
| `estado.py` | roda a rede e cospe o `/api/texugo` que os testes do Cérebro usam |
| `mede.py` | peso − média da coluna, no nascimento e depois de aprender |
| `piso.py` | qual piso separa gosto aprendido de ruído de nascença (deu 0,20) |
| `inib.py` | se a inibição lateral informa alguma coisa instante a instante |
| `teste-atualizar.sh` | o `atualizar-painel.sh` contra remoto, `systemctl` e `curl` falsos |

## Como rodar

```sh
CHROME=$(command -v chromium || command -v google-chrome)
python3 -m http.server 8799 --bind 127.0.0.1 --directory testes/_saida &

python3 testes/estado.py 20 > testes/_saida/texugo-velho.json   # cérebro treinado
python3 testes/estado.py  0 > testes/_saida/texugo-novo.json    # recém-nascido
python3 testes/monta-cerebro.py index.html
"$CHROME" --headless=new --window-size=1920,1240 --virtual-time-budget=5000 \
  --dump-dom http://127.0.0.1:8799/teste-cerebro.html | grep -o '"erros":\[[^]]*\]'

python3 testes/monta-telas.py index.html --real   # + as telas do Linha com o dado da propria maquina
"$CHROME" --headless=new --window-size=1920,1080 --virtual-time-budget=6000 \
  --screenshot=/tmp/tela.png http://127.0.0.1:8799/teste-linha-1.html

bash testes/teste-atualizar.sh atualizar-painel.sh
```

`--screenshot=arquivo.png` no lugar do `--dump-dom` tira o print — foi o print que pegou dois
defeitos de layout que o relatório não pegava.

## Pegadinhas

- O editor escuta `pointerdown`, não `click`: `.click()` sintético não dispara nada.
- `setPointerCapture` com `pointerId` sintético estoura `NotFoundError` e mata o resto do handler
  — nos roteiros ele vira no-op.
- Teste de reload quer o MESMO `--user-data-dir` nas duas chamadas, senão o `localStorage` nasce
  vazio na segunda.
- **A janela do print não é a janela do relatório.** O `--screenshot` redimensiona a PÁGINA pro
  tamanho do print (`--window-size=1920,1080` → viewport de 1080, que é o monitor do painel),
  enquanto o `--dump-dom` deixa o Chrome descontar ~87 px de janela (`--window-size=1920,1167` →
  viewport de 1080). Misturar os dois faz o print mostrar cartões 40 px mais altos que o relatório
  e parece bug de grade que não existe.
- **Cartão não desenhado não é erro.** O `renderDashB` engole a exceção de um medidor e um medidor
  que nunca foi desenhado não gera exceção nenhuma: o cartão fica só com o rótulo. Por isso o
  relatório do `monta-telas.py` traz três checagens que não são de erro — `desenho` (o cartão tem
  conteúdo?), `muda` (o conteúdo acompanha o dado, quando o dado muda?) e `traco` (a polilinha tem
  geometria?). Cada uma delas já pegou um defeito que passou por print e por `"erros":[]`.
- O relatório do `monta-telas.py` só mede depois de 5,2 s de tempo virtual de propósito: antes
  disso o layout ainda é o da fonte de reserva, e as alturas não são as da tela.
