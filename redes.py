"""Contadores das redes sociais pro painel.

Credenciais em ~/.config/toca-do-texugo/redes.json (fora do git; relido quando muda).
Historico diario em ~/.config/toca-do-texugo/redes-historico.json (pra "+N hoje" e a tendencia de 30 dias).
"""
import datetime
import hashlib
import json
import secrets
import subprocess
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

CONF = Path.home() / ".config/toca-do-texugo/redes.json"
HIST = Path.home() / ".config/toca-do-texugo/redes-historico.json"
TOKENS = Path.home() / ".config/toca-do-texugo/redes-tokens.json"  # tokens renovados automaticamente
HIST_DAYS = 30
TRACKED = ("followers", "views", "likes")


class ApiError(Exception):
    pass


def _get(url, headers=None, data=None):
    req = urllib.request.Request(url, data=data, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        # So a mensagem da API: a URL pode ter a chave e nunca vai pro navegador
        try:
            err = json.loads(e.read() or b"{}")
            msg = err.get("error", {}).get("message") if isinstance(err.get("error"), dict) else err.get("message")
        except ValueError:
            msg = None
        raise ApiError(f"HTTP {e.code}" + (f": {msg}" if msg else "")) from None
    except (urllib.error.URLError, TimeoutError) as e:
        raise ApiError(f"sem conexão ({getattr(e, 'reason', e)})") from None


def _int(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return 0


def _q(**kw):
    return urllib.parse.urlencode({k: v for k, v in kw.items() if v is not None})


class Youtube:
    interval = 600  # cada leitura custa ~5 unidades da cota diaria de 10.000
    API = "https://www.googleapis.com/youtube/v3/"

    def __init__(self, cfg):
        self.cfg = cfg

    def configured(self):
        return bool(self.cfg.get("api_key") and self.cfg.get("handle"))

    def fetch(self):
        key = self.cfg["api_key"]
        d = _get(self.API + "channels?" + _q(part="snippet,statistics,contentDetails", forHandle=self.cfg["handle"], key=key))
        if not d.get("items"):
            raise ApiError(f"canal {self.cfg['handle']} não encontrado")
        ch = d["items"][0]
        st = ch["statistics"]
        # Likes: a API nao da o total do canal, entao soma video por video
        ids, token = [], None
        while len(ids) < 500:
            page = _get(self.API + "playlistItems?" + _q(part="contentDetails", maxResults=50, pageToken=token, key=key,
                                                          playlistId=ch["contentDetails"]["relatedPlaylists"]["uploads"]))
            ids += [it["contentDetails"]["videoId"] for it in page.get("items", [])]
            token = page.get("nextPageToken")
            if not token:
                break
        likes, videos = 0, {}
        for i in range(0, len(ids), 50):
            for v in _get(self.API + "videos?" + _q(part="statistics,snippet", id=",".join(ids[i:i + 50]), key=key)).get("items", []):
                likes += int(v["statistics"].get("likeCount", 0))
                videos[v["id"]] = v
        latest = videos.get(ids[0]) if ids else None
        return {
            "name": ch["snippet"]["title"],
            "handle": self.cfg["handle"],
            "followers": int(st.get("subscriberCount", 0)),
            "views": int(st.get("viewCount", 0)),
            "likes": likes,
            "posts": int(st.get("videoCount", 0)),
            "latest": latest and {
                "title": latest["snippet"]["title"],
                "views": int(latest["statistics"].get("viewCount", 0)),
                "likes": int(latest["statistics"].get("likeCount", 0)),
                "published": latest["snippet"]["publishedAt"],
            },
        }


class Twitch:
    interval = 60  # rapido pra perceber quando a live comeca
    API = "https://api.twitch.tv/helix/"

    def __init__(self, cfg):
        self.cfg = cfg
        self.token = None
        self.user = None

    def configured(self):
        return bool(self.cfg.get("client_id") and self.cfg.get("client_secret") and self.cfg.get("login"))

    def _helix(self, path):
        for _ in range(2):
            if not self.token:
                self.token = _get("https://id.twitch.tv/oauth2/token", data=_q(
                    client_id=self.cfg["client_id"], client_secret=self.cfg["client_secret"],
                    grant_type="client_credentials").encode())["access_token"]
            try:
                return _get(self.API + path, {"Client-Id": self.cfg["client_id"], "Authorization": "Bearer " + self.token})
            except ApiError as e:
                if not str(e).startswith("HTTP 401"):
                    raise
                self.token = None  # token venceu: pede outro e tenta de novo
        raise ApiError("token recusado pela Twitch")

    def fetch(self):
        if not self.user:
            users = self._helix("users?" + _q(login=self.cfg["login"])).get("data") or []
            if not users:
                raise ApiError(f"usuário {self.cfg['login']} não encontrado")
            self.user = users[0]
        uid = self.user["id"]
        followers = self._helix("channels/followers?" + _q(broadcaster_id=uid))["total"]
        live = (self._helix("streams?" + _q(user_id=uid)).get("data") or [None])[0]
        return {
            "name": self.user["display_name"],
            "handle": self.cfg["login"],
            "followers": followers,
            "live": live and {
                "title": live["title"],
                "game": live["game_name"],
                "viewers": live["viewer_count"],
                "started": live["started_at"],
            },
        }


class Kick:
    """Kick pelo endpoint que o proprio site usa (kick.com/api/v2), sem credencial nenhuma.

    A API oficial (api.kick.com) nao devolve numero de seguidores, so a live; como o card e de
    seguidores, aqui vai o v2. Nao e documentado: pode mudar ou passar a barrar. O Cloudflare do
    site recusa o urllib (403), entao a leitura vai por `curl`, que ja e dependencia do projeto.
    """
    interval = 60  # rapido pra perceber quando a live comeca, igual a Twitch
    API = "https://kick.com/api/v2/channels/"

    def __init__(self, cfg):
        self.cfg = cfg

    def configured(self):
        return bool(self.cfg.get("usuario"))

    def fetch(self):
        slug = self.cfg["usuario"].lstrip("@").lower()
        out = subprocess.run(["curl", "-sS", "--max-time", "15", "--fail", self.API + urllib.parse.quote(slug)],
                             capture_output=True, text=True)
        if out.returncode != 0:
            if "404" in out.stderr:
                raise ApiError(f"canal {slug} não encontrado")
            raise ApiError("curl falhou" + (f": {out.stderr.strip()[:80]}" if out.stderr.strip() else ""))
        try:
            d = json.loads(out.stdout)
        except ValueError:
            raise ApiError("resposta não era JSON (o Kick pode ter mudado o endpoint)") from None
        live = d.get("livestream") or None
        cat = (live or {}).get("categories") or []
        return {
            "name": (d.get("user") or {}).get("username") or slug,
            "handle": slug,
            "followers": _int(d.get("followers_count")),  # o Kick manda como string
            "live": live and {
                "title": live.get("session_title"),
                "game": cat[0].get("name") if cat else None,
                "viewers": _int(live.get("viewer_count")),
                # Vem "2026-09-28 13:07:36" em UTC, sem fuso: vira ISO pro painel nao errar 3 h
                "started": (live.get("start_time") or "").replace(" ", "T") + "Z" if live.get("start_time") else None,
            },
        }


def _tokens():
    try:
        return json.loads(TOKENS.read_text())
    except (OSError, ValueError):
        return {}


def _save_tokens(data):
    TOKENS.touch(mode=0o600, exist_ok=True)
    TOKENS.write_text(json.dumps(data))


class TikTok:
    """Login Kit Desktop + Display API. Autoriza uma vez em /tiktok/login; o servidor guarda e renova os tokens."""
    interval = 900
    API = "https://open.tiktokapis.com/v2/"
    REDIRECT = "http://localhost:8787/tiktok/callback/"
    SCOPES = "user.info.basic,user.info.stats,video.list"
    _pending = {}  # state -> code_verifier (PKCE), sobrevive a recarga da config

    def __init__(self, cfg):
        self.cfg = cfg
        # Tem que ser identico ao cadastrado no Login Kit (Desktop) do app/sandbox
        self.redirect = cfg.get("redirect_uri") or self.REDIRECT

    def configured(self):
        return bool(self.cfg.get("client_key") and self.cfg.get("client_secret"))

    def login_url(self):
        verifier = secrets.token_urlsafe(48)[:64]
        state = secrets.token_urlsafe(16)
        TikTok._pending = {state: verifier}
        return "https://www.tiktok.com/v2/auth/authorize/?" + _q(
            client_key=self.cfg["client_key"], response_type="code", scope=self.SCOPES,
            redirect_uri=self.redirect, state=state, code_challenge_method="S256",
            code_challenge=hashlib.sha256(verifier.encode()).hexdigest())  # TikTok usa hex, nao base64url

    def _token_call(self, **params):
        r = _get(self.API + "oauth/token/", {"Content-Type": "application/x-www-form-urlencoded"},
                 _q(client_key=self.cfg["client_key"], client_secret=self.cfg["client_secret"], **params).encode())
        if "access_token" not in r:
            raise ApiError(r.get("error_description") or r.get("error") or "TikTok recusou o token")
        now = time.time()
        store = _tokens()
        store["tiktok"] = {"client_key": self.cfg["client_key"], "access_token": r["access_token"],
                           "expires_at": now + r.get("expires_in", 86400),
                           "refresh_token": r["refresh_token"], "refresh_expires_at": now + r.get("refresh_expires_in", 365 * 86400)}
        _save_tokens(store)
        return store["tiktok"]

    def finish_login(self, code, state):
        verifier = TikTok._pending.pop(state, None)
        if not verifier:
            raise ApiError("login expirado ou state inválido; abra /tiktok/login de novo")
        self._token_call(code=code, grant_type="authorization_code", redirect_uri=self.redirect, code_verifier=verifier)

    def _access(self):
        tok = _tokens().get("tiktok")
        if not tok or tok.get("client_key") != self.cfg["client_key"]:
            raise ApiError("falta autorizar: abra http://localhost:8787/tiktok/login no navegador do PC")
        if time.time() > tok["refresh_expires_at"]:
            raise ApiError("autorização venceu: abra http://localhost:8787/tiktok/login de novo")
        if time.time() > tok["expires_at"] - 3600:
            tok = self._token_call(grant_type="refresh_token", refresh_token=tok["refresh_token"])
        return {"Authorization": "Bearer " + tok["access_token"]}

    def _api(self, path, body=None):
        h = self._access()
        if body is not None:
            h["Content-Type"] = "application/json"
        r = _get(self.API + path, h, json.dumps(body).encode() if body is not None else None)
        err = r.get("error") or {}
        if err.get("code") not in (None, "ok"):
            raise ApiError(err.get("message") or err["code"])
        return r.get("data") or {}

    def fetch(self):
        u = self._api("user/info/?" + _q(fields="open_id,display_name,follower_count,likes_count,video_count")).get("user", {})
        videos, cursor = [], None
        while len(videos) < 500:
            page = self._api("video/list/?" + _q(fields="id,title,view_count,like_count,comment_count,create_time"),
                             {"max_count": 20, **({"cursor": cursor} if cursor else {})})
            videos += page.get("videos", [])
            if not page.get("has_more"):
                break
            cursor = page.get("cursor")
        views = sum(v.get("view_count", 0) for v in videos)
        latest = max(videos, key=lambda v: v.get("create_time", 0)) if videos else None
        return {
            "name": u.get("display_name"),
            "handle": self.cfg.get("usuario"),
            "followers": u.get("follower_count", 0),
            "likes": u.get("likes_count", 0),
            "views": views,
            "posts": u.get("video_count", 0),
            "latest": latest and {
                "title": (latest.get("title") or "").split("\n")[0][:120],
                "views": latest.get("view_count", 0),
                "likes": latest.get("like_count", 0),
                "comments": latest.get("comment_count", 0),
            },
        }


PROVIDERS = {"youtube": Youtube, "twitch": Twitch, "kick": Kick, "tiktok": TikTok}


class Redes:
    def __init__(self):
        self.data = {}
        self._mtime = None
        self._providers = {}
        self._next = {}
        try:
            self.hist = json.loads(HIST.read_text())
        except (OSError, ValueError):
            self.hist = {}
        threading.Thread(target=self._loop, daemon=True).start()

    def _load_config(self):
        try:
            mtime = CONF.stat().st_mtime
        except OSError:
            mtime = None
        if mtime == self._mtime:
            return
        self._mtime = mtime
        try:
            cfg = json.loads(CONF.read_text()) if mtime else {}
        except (OSError, ValueError):
            cfg = {}
        # Config mudou: recria tudo e busca de novo ja
        self._providers = {name: cls(cfg.get(name, {})) for name, cls in PROVIDERS.items()}
        self._next = {}

    def _loop(self):
        while True:
            self._load_config()
            now = time.time()
            for name, prov in self._providers.items():
                if now < self._next.get(name, 0):
                    continue
                self._next[name] = now + prov.interval
                handle = prov.cfg.get("handle") or prov.cfg.get("login") or prov.cfg.get("usuario")
                if not prov.configured():
                    self.data[name] = {"configured": False, "handle": handle}
                    continue
                try:
                    vals = prov.fetch()
                    self._record(name, vals)
                    self.data[name] = {"configured": True, "ok": True, "updated": now, **vals, **self._trend(name)}
                except Exception as exc:  # erro de rede/API nao pode derrubar a thread
                    prev = self.data.get(name, {})
                    self.data[name] = {**prev, "configured": True, "ok": False, "handle": handle, "error": str(exc)[:200]}
                    self._next[name] = now + min(prov.interval, 120)
            time.sleep(10)

    def provider(self, name):
        self._load_config()
        return self._providers.get(name)

    def refresh_now(self, name):
        self._next[name] = 0

    def _record(self, name, vals):
        day = datetime.date.today().isoformat()
        days = self.hist.setdefault(name, {})
        entry = days.setdefault(day, {})
        for k in TRACKED:
            if isinstance(vals.get(k), int):
                entry.setdefault(k, [vals[k], vals[k]])[1] = vals[k]  # [primeiro, ultimo] do dia
        for old in sorted(days)[:-HIST_DAYS]:
            del days[old]
        try:
            HIST.write_text(json.dumps(self.hist))
        except OSError:
            pass

    def _trend(self, name):
        days = self.hist.get(name, {})
        order = sorted(days)
        if not order:
            return {}
        today, prev = days[order[-1]], (days[order[-2]] if len(order) > 1 else None)
        delta = {}
        for k, (first, last) in today.items():
            base = prev[k][1] if prev and k in prev else first
            delta[k] = last - base
        return {"today": delta, "series": [days[d].get("followers", [None, None])[1] for d in order]}
