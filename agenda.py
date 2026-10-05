"""Agenda e lembretes pro painel, alimentados por um bot do Telegram.

Credencial em ~/.config/toca-do-texugo/agenda.json (fora do git):

    {"bot_token": "123456:ABC-DEF...", "chat_id": 12345678}

O bot e publico por natureza: qualquer pessoa que descubra o nome dele consegue mandar
mensagem. Por isso TUDO que nao vier do `chat_id` configurado e descartado sem olhar o texto.

O fluxo e so de entrada: o painel le as mensagens com getUpdates e nunca escreve de volta.
Marcar como feito e estado local, guardado em ~/.config/toca-do-texugo/agenda-itens.json junto
com o offset do getUpdates (pra nao reler o que ja virou item depois de um reinicio).
"""
import json
import re
import threading
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

CONF = Path.home() / ".config/toca-do-texugo/agenda.json"
ITENS = Path.home() / ".config/toca-do-texugo/agenda-itens.json"
API = "https://api.telegram.org/bot"
ESPERA = 50       # long polling: a chamada fica aberta esperando mensagem nova
GUARDA_DIAS = 7   # item feito some da lista depois disso
MAX_ITENS = 200   # teto do arquivo, pro historico nao crescer sem fim

DIAS = ("segunda", "terca", "quarta", "quinta", "sexta", "sabado", "domingo")


def _sem_acento(s):
    return "".join(c for c in unicodedata.normalize("NFD", s.lower()) if unicodedata.category(c) != "Mn")


def _quando(texto):
    """Tira do comeco do texto uma data/hora em portugues e devolve (timestamp, resto).

    Entende "hoje", "amanha", nome do dia da semana, "dd/mm" e hora em "14h", "14h30" ou
    "14:30". Sem nada reconhecido, devolve (None, texto): vira recado sem hora, nao erro.
    """
    bruto = texto.strip()
    chave = _sem_acento(bruto)
    agora = datetime.now()
    dia, corte = None, 0

    m = re.match(r"(hoje|amanha|depois de amanha)\b", chave)
    if m:
        dia = agora + timedelta(days={"hoje": 0, "amanha": 1, "depois de amanha": 2}[m.group(1)])
        corte = m.end()
    if dia is None:
        m = re.match(r"(?:(?:na|no)\s+)?(" + "|".join(DIAS) + r")(?:-feira)?\b", chave)
        if m:
            # Proxima ocorrencia daquele dia da semana; hoje mesmo nao conta
            delta = (DIAS.index(m.group(1)) - agora.weekday()) % 7 or 7
            dia = agora + timedelta(days=delta)
            corte = m.end()
    if dia is None:
        m = re.match(r"(\d{1,2})/(\d{1,2})(?:/(\d{2,4}))?\b", chave)
        if m:
            d, mes = int(m.group(1)), int(m.group(2))
            ano = int(m.group(3) or agora.year)
            if ano < 100:
                ano += 2000
            try:
                dia = agora.replace(year=ano, month=mes, day=d)
            except ValueError:
                return None, bruto
            corte = m.end()
    if dia is None:
        return None, bruto

    resto = bruto[corte:].lstrip(" ,-–:")
    hora = re.match(r"(?:as\s+)?(\d{1,2})(?:[h:](\d{2})?)\b", _sem_acento(resto))
    if hora:
        h, mi = int(hora.group(1)), int(hora.group(2) or 0)
        if h < 24 and mi < 60:
            dia = dia.replace(hour=h, minute=mi)
            resto = resto[hora.end():].lstrip(" ,-–")
    else:
        dia = dia.replace(hour=9, minute=0)  # sem hora dita, o compromisso cai de manha
    return dia.replace(second=0, microsecond=0).timestamp(), resto.strip() or bruto


class Agenda:
    def __init__(self):
        self.state = {"ligado": False}
        self._itens = []
        self._offset = 0
        self._erro = None
        self._lock = threading.Lock()
        self._carrega()
        if self._conf():
            self.state = {"ligado": True}
            threading.Thread(target=self._loop, daemon=True).start()
        self._publica()

    # --- disco ---
    def _conf(self):
        try:
            c = json.loads(CONF.read_text())
            return c if c.get("bot_token") and c.get("chat_id") is not None else None
        except (OSError, ValueError, AttributeError):
            return None

    def _carrega(self):
        try:
            d = json.loads(ITENS.read_text())
            self._itens = [i for i in d.get("itens", []) if isinstance(i, dict)]
            self._offset = int(d.get("offset", 0))
        except (OSError, ValueError, TypeError):
            self._itens, self._offset = [], 0

    def _grava(self):
        ITENS.parent.mkdir(parents=True, exist_ok=True)
        ITENS.touch(mode=0o600, exist_ok=True)
        ITENS.write_text(json.dumps({"offset": self._offset, "itens": self._itens}))

    # --- telegram ---
    def _chama(self, metodo, **params):
        c = self._conf()
        if not c:
            return None
        url = f"{API}{c['bot_token']}/{metodo}?" + urllib.parse.urlencode(params)
        with urllib.request.urlopen(url, timeout=ESPERA + 15) as r:
            d = json.load(r)
        return d.get("result") if d.get("ok") else None

    def _loop(self):
        while True:
            try:
                updates = self._chama("getUpdates", offset=self._offset, timeout=ESPERA,
                                      allowed_updates='["message"]')
                if updates:
                    with self._lock:
                        for u in updates:
                            self._offset = max(self._offset, u.get("update_id", 0) + 1)
                            self._absorve(u.get("message") or {})
                        self._limpa()
                        self._grava()
                    self._publica()
                self._erro = None
            except urllib.error.HTTPError as e:
                # So o codigo: a URL carrega o token do bot e nao pode ir pro painel
                self._erro = f"Telegram respondeu {e.code}"
                self._publica()
                time.sleep(60)
            except (OSError, ValueError, TypeError) as e:
                self._erro = type(e).__name__
                self._publica()
                time.sleep(30)

    def _absorve(self, msg):
        c = self._conf()
        # Unico filtro que importa: mensagem de qualquer outro chat e descartada sem ler o texto
        if not c or (msg.get("chat") or {}).get("id") != c["chat_id"]:
            return
        texto = (msg.get("text") or "").strip()
        if not texto or texto.startswith("/"):
            return
        quando, resto = _quando(texto)
        self._itens.append({
            "id": str(msg.get("message_id")),
            "texto": resto[:200],
            "quando": quando,
            "feito": False,
            "criado": msg.get("date") or time.time(),
        })

    def _limpa(self):
        limite = time.time() - GUARDA_DIAS * 86400
        self._itens = [i for i in self._itens if not (i.get("feito") and (i.get("feito_em") or 0) < limite)]
        del self._itens[:-MAX_ITENS]

    # --- painel ---
    def feito(self, item_id, valor=True):
        with self._lock:
            for i in self._itens:
                if i.get("id") == item_id:
                    i["feito"] = bool(valor)
                    i["feito_em"] = time.time() if valor else None
                    self._grava()
                    self._publica()
                    return True
        return False

    def _publica(self):
        if not self._conf():
            self.state = {"ligado": False}
            return
        # Compromisso com hora primeiro, por data; recado solto depois, mais novo em cima
        com_hora = sorted([i for i in self._itens if i.get("quando")], key=lambda i: i["quando"])
        sem_hora = sorted([i for i in self._itens if not i.get("quando")],
                          key=lambda i: i.get("criado", 0), reverse=True)
        self.state = {"ligado": True, "erro": self._erro, "itens": com_hora + sem_hora}
