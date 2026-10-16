#!/usr/bin/env python3
"""Cerebro do texugo: rede de neuronios com spike e STDP no lugar da tabela de probabilidades.

Inspirado no DeskBuddy (@jackyfernandess no TikTok): em vez de um LLM, ou de uma regra escrita a
mao pra cada reacao, os sinais do painel viram trens de spike e a plasticidade sinaptica decide
sozinha qual sinal passa a puxar qual comportamento. O painel so desenha o resultado.

    sensores -> 16 neuronios de entrada (Poisson: taxa proporcional ao sinal)
             -> 6 neuronios de saida (LIF com limiar adaptativo), um por comportamento
             -> inibicao lateral: quem dispara primeiro cala os outros (winner-take-all)

A cada passo de 10 ms (a janela do STDP e de ~20 ms: a 1x/s do Collector tudo seria simultaneo):

    STDP          entrada que dispara ANTES da saida fortalece a sinapse; depois dela, enfraquece
    normalizacao  a soma dos pesos que chegam num neuronio e constante -> as entradas competem
    homeostase    o limiar sobe em quem dispara demais e desce em quem dispara de menos

As duas ultimas garantem que nenhum comportamento morra pra sempre nem domine pra sempre: o bicho
vai mudando de personalidade com o tempo, mas nunca fica so dormindo. Nao ha recompensa nem
supervisao: afagar o texugo no painel nao treina nada, de proposito.

O cerebro mora em ~/.config/toca-do-texugo/texugo-cerebro.json (pesos, limiares, idade) pra
aprendizagem sobreviver a reiniciar o servico.
"""
import json
import math
import random
import threading
import time
from pathlib import Path

CEREBRO = Path.home() / ".config/toca-do-texugo/texugo-cerebro.json"

DT = 0.01               # passo da simulacao (100 Hz)
TAU_MEMBRANA = 0.02     # vazamento do potencial de membrana
TAU_TRACO = 0.02        # memoria curta do STDP, de cada lado da sinapse
GANHO = 1.0             # quanto cada spike de entrada carrega a membrana, por unidade de peso
W_MIN, W_MAX = 0.01, 1.0  # piso > 0: sensor nenhum morre de vez, sempre pode voltar
W_SOMA = 2.4            # soma dos pesos que chegam em cada neuronio de saida (normalizacao)
# STDP so no pos-spike (Diehl & Cook 2015), nao em par pre/pos. E de proposito: a depressao por
# spike de ENTRADA e proporcional a taxa do sensor, nao a correlacao, e enterra justamente os
# sensores mais ativos (cpu, rede, musica) enquanto a normalizacao infla os quietos. Assim toda
# atualizacao acontece no mesmo instante -- o do disparo -- e as entradas competem por chegar
# JUNTO com ele: quem estava ativo potencia, quem estava quieto deprime.
# E regra de COVARIANCIA (Sejnowski), nao um limiar fixo: cada sensor e comparado com a propria
# media historica. Com limiar fixo, sensor ligado quase sempre (cpu, volume) domina todos os
# neuronios -- todos aprendem a media -- e sensor que marca UMA situacao (rede no download) e
# deprimido nas outras tres e morre antes de conseguir especializar alguem. Contra a propria
# media, o sempre-ligado fica neutro e quem ensina e o "ligado agora, normalmente nao".
ETA_STDP = 0.004        # passo por disparo; devagar de proposito (personalidade em horas)
TAU_MEDIA = 60.0        # janela do "normalmente" de cada sensor
TAXA_ALVO = 4.0         # Hz que a homeostase persegue em cada neuronio de saida
TAU_TAXA = 45.0         # janela da media de disparo: longa perto do dominio de 1.5 s (pra ele
                        # acontecer), curta o bastante pra homeostase reagir em menos de um minuto
ETA_LIMIAR = 0.001      # mais lenta que a inibicao de proposito: senao a homeostase derruba o
                        # vencedor antes do STDP afinar nada, e ninguem se especializa
# O teto e so salvaguarda, nao faixa de operacao: neuronio ligado nos sensores sempre ativos
# (cpu, gpu) precisa de limiar alto pra ficar no alvo, e limiar grudado no teto = homeostase
# desligada -- ele dispara acima do alvo e passa a vencer o voto em qualquer situacao.
LIMIAR_MIN, LIMIAR_MAX = 0.1, 60.0
REFRATARIO = 0.03       # curto de proposito: quem venceu PRECISA poder vencer de novo (ver abaixo)
# Inibicao lateral que DURA, e nao um desconto de um passo so. E ela que cria personalidade: sem
# isso todos os neuronios disparam em toda situacao e aprendem a mesma media, e o comportamento
# volta a ser sorteio. Quem vence cala os outros por ~TAU_INIB e segue vencendo enquanto a
# situacao durar -- entao o STDP afina ESSE neuronio pra ESSA situacao. Quem tira o vencedor do
# trono depois e a homeostase, nao o rival.
INIB_FORCA = 0.6        # quanto o vencedor cala os outros; 0.9 era total demais -- quem pegava o
                        # trono primeiro segurava mesmo sem a situacao ser dele
# TETO da inibicao, e ele e essencial: a inibicao ACUMULA (um disparo em cima do outro), entao
# sem teto < 1 os perdedores chegam a 1.0 e, numa inibicao divisiva, 1.0 e surdez permanente --
# carga x (1-1) = 0. Eles nunca mais disparam, nem com o limiar no piso. Com 0.8 sempre passa um
# quinto do estimulo, e quem esta na situacao certa consegue furar o bloqueio.
INIB_MAX = 0.8
# O trono tem que durar na ordem do COMPORTAMENTO (segundos), nao de milissegundos: a situacao no
# painel dura dezenas de segundos, e com inibicao curta todos os 6 disparam dentro da mesma
# situacao e voltam a aprender a media. 2 s tambem e a escala em que o bicho troca de ideia.
TAU_INIB = 1.5          # tempo pro calado voltar a ouvir
# A janela do voto precisa de spike suficiente pra z significar algo: a 2 Hz em 2 s sao 4 spikes,
# e 2 de diferenca ja davam z=0.8 (ruido virava escolha). 5 s a 4 Hz sao ~20.
TAU_VOTO = 5.0          # janela que decide o comportamento vigente
R_MIN, R_MAX = 2.0, 60.0  # Hz de um sensor em 0 e em 1
TAU_FASICO = 0.5        # decaimento dos sensores de "mudou agora"
SALVA_CADA = 60.0       # segundos entre gravacoes do cerebro
PUBLICA_CADA = 10       # passos entre atualizacoes do self.state (10 Hz)

# Um neuronio de saida por comportamento, com a faixa de duracao em segundos. A rede escolhe QUAL;
# a duracao sai da confianca da escolha (margem sobre o segundo colocado).
COMPORTAMENTOS = {
    "andar": (3.0, 9.0),
    "pular": (0.0, 0.0),
    "parar": (2.0, 6.0),
    "sentar": (5.0, 15.0),
    "dormir": (20.0, 90.0),
    "dancar": (6.0, 20.0),
}

# Sensores: 10 tonicos (nivel) + 6 fasicos (mudanca). Nome -> rotulo pro painel.
SENSORES = {
    "cpu": "CPU",
    "gpu": "GPU",
    "calor": "calor",
    "mem": "memória",
    "rede": "rede",
    "disco": "disco",
    "musica": "música",
    "volume": "volume",
    "claude": "Claude",
    "noite": "noite",
    "pico_cpu": "pico de CPU",
    "pico_rede": "pico de rede",
    "pico_disco": "pico de disco",
    "troca_musica": "trocou a música",
    "agenda": "agenda nova",
    "live": "live no ar",
}
FASICOS = ("pico_cpu", "pico_rede", "pico_disco", "troca_musica", "agenda", "live")


def _lim(v, a=0.0, b=1.0):
    return a if v < a else (b if v > b else v)


def _log_bps(bps):
    """Vazao em bytes/s pra 0..1 numa escala log (1 ~= 100 MB/s)."""
    return _lim(math.log10(1.0 + max(0.0, bps)) / 8.0)


class Sensores:
    """Transforma o /api/stats num vetor de 0..1 por canal.

    Os canais tonicos seguem o nivel do sinal. Os fasicos sao pulsos: nascem 1 quando a coisa
    muda e decaem em ~TAU_FASICO, porque e a MUDANCA que o bicho precisa sentir (foi o que o
    DeskBuddy fazia com os pixels da tela).
    """

    def __init__(self):
        self.valores = {k: 0.0 for k in SENSORES}
        self._ant = {}
        self._t_stats = None

    def ler(self, stats, extra, dt):
        for k in FASICOS:  # pulso sempre decaindo, mesmo sem stats novo
            self.valores[k] *= math.exp(-dt / TAU_FASICO)
        if stats and stats.get("t") != self._t_stats:
            self._t_stats = stats.get("t")
            try:
                self._absorve(stats, extra or {})
            except Exception:  # stats incompleto nunca derruba o cerebro
                pass
        return self.valores

    def _absorve(self, s, extra):
        v, ant = self.valores, self._ant
        cpu = (s.get("cpu") or {}).get("pct") or 0.0
        gpu = (s.get("gpu") or {}).get("util") or 0.0
        temps = [(s.get("cpu") or {}).get("temp"), (s.get("gpu") or {}).get("temp")]
        net = s.get("net") or {}
        dio = s.get("diskio") or {}
        mid = s.get("media") or {}
        vol = s.get("volume") or {}
        cla = s.get("claude") or {}

        rede = _log_bps((net.get("rx") or 0.0) + (net.get("tx") or 0.0))
        disco = _log_bps((dio.get("read") or 0.0) + (dio.get("write") or 0.0))

        v["cpu"] = _lim(cpu / 100.0)
        v["gpu"] = _lim(gpu / 100.0)
        v["calor"] = _lim((max([t for t in temps if t] or [0]) - 45.0) / 40.0)
        v["mem"] = _lim(((s.get("mem") or {}).get("pct") or 0.0) / 100.0)
        v["rede"] = rede
        v["disco"] = disco
        v["musica"] = 1.0 if mid.get("status") == "Playing" else 0.0
        v["volume"] = 0.0 if vol.get("muted") else _lim((vol.get("pct") or 0) / 100.0)
        v["claude"] = _lim((cla.get("five_hour") or 0) / 100.0)
        hora = time.localtime().tm_hour + time.localtime().tm_min / 60.0
        v["noite"] = 0.5 - 0.5 * math.cos(2 * math.pi * (hora - 3.0) / 24.0)

        # Fasicos: so sobem, e so quando a coisa muda pra cima.
        v["pico_cpu"] = max(v["pico_cpu"], _lim((cpu - ant.get("cpu", cpu)) / 25.0))
        v["pico_rede"] = max(v["pico_rede"], _lim((rede - ant.get("rede", rede)) * 4.0))
        v["pico_disco"] = max(v["pico_disco"], _lim((disco - ant.get("disco", disco)) * 4.0))
        titulo = mid.get("title") or ""
        if titulo and "titulo" in ant and titulo != ant["titulo"]:
            v["troca_musica"] = 1.0
        itens = extra.get("agenda_itens")
        if itens is not None and itens > ant.get("agenda_itens", itens):
            v["agenda"] = 1.0
        if extra.get("live") and not ant.get("live"):
            v["live"] = 1.0

        ant.update(cpu=cpu, rede=rede, disco=disco, titulo=titulo,
                   agenda_itens=itens if itens is not None else ant.get("agenda_itens"),
                   live=extra.get("live"))


class Texugo:
    """A rede em si, numa thread propria a 100 Hz.

    `fonte` e um chamavel que devolve (stats, extra); extra aceita "agenda_itens" e "live". A
    classe nunca importa o server, pra poder rodar sozinha (ver `python3 texugo.py`).
    """

    def __init__(self, fonte=None):
        self.fonte = fonte or (lambda: ({}, {}))
        self.nomes = list(COMPORTAMENTOS)
        self.sensores = Sensores()
        # Nasce no instinto de proposito: a chave de modo mora no medidor "Cerebro", que nao esta
        # no layout padrao -- vir ligado trocaria o comportamento do mascote sem o dono ter onde
        # desligar. A rede APRENDE desde o boot nos dois modos; o modo so decide quem comanda.
        self.modo = "instinto"
        self.state = {"modo": self.modo, "comportamento": "parar", "idade": 0.0}
        self._trava = threading.Lock()
        self._n_in, self._n_out = len(SENSORES), len(self.nomes)
        self._zera()
        self._carrega()
        threading.Thread(target=self._loop, daemon=True).start()

    # ---------- estado da rede ----------

    def _zera(self):
        n_in, n_out = self._n_in, self._n_out
        # Peso inicial sorteado em volta da media que a normalizacao impoe: ninguem nasce dono.
        media = W_SOMA / n_in
        self.pesos = [[_lim(random.gauss(media, media * 0.3), W_MIN, W_MAX) for _ in range(n_in)]
                      for _ in range(n_out)]
        self._normaliza()
        self.limiares = [1.0] * n_out
        # Comeca NO alvo, nao em zero: com taxa zerada a homeostase le "todos abaixo do alvo",
        # joga os limiares no piso em 2 s e o primeiro que dispara segura o trono por minutos.
        self.taxas = [TAXA_ALVO] * n_out
        self.v = [0.0] * n_out
        self.traco_pre = [0.0] * n_in
        self.media_pre = [0.0] * n_in
        self.traco_pos = [0.0] * n_out
        self.votos = [0.0] * n_out
        self.refratario = [0.0] * n_out
        self.inib = [0.0] * n_out
        self.taxas_in = [0.0] * n_in
        self.idade = 0.0
        self.spikes = 0

    def _normaliza(self):
        for linha in self.pesos:
            s = sum(linha)
            if s > 1e-9:
                k = W_SOMA / s
                for j in range(len(linha)):
                    linha[j] = _lim(linha[j] * k, W_MIN, W_MAX)

    # ---------- um passo de 10 ms ----------

    def passo(self, stats, extra):
        decai_v = math.exp(-DT / TAU_MEMBRANA)
        decai_tr = math.exp(-DT / TAU_TRACO)
        decai_voto = math.exp(-DT / TAU_VOTO)
        decai_inib = math.exp(-DT / TAU_INIB)
        decai_taxa = DT / TAU_TAXA

        sens = self.sensores.ler(stats, extra, DT)
        self.idade += DT

        # 1. entradas: Poisson com taxa proporcional ao sinal
        entrou = []
        for j, nome in enumerate(SENSORES):
            x = _lim(sens.get(nome, 0.0))
            taxa = R_MIN + (R_MAX - R_MIN) * x
            self.taxas_in[j] += (taxa - self.taxas_in[j]) * decai_taxa
            self.traco_pre[j] *= decai_tr
            if random.random() < taxa * DT:
                self.traco_pre[j] = 1.0
                entrou.append(j)
            self.media_pre[j] += (self.traco_pre[j] - self.media_pre[j]) * (DT / TAU_MEDIA)

        # 2. membrana dos neuronios de saida
        for i in range(self._n_out):
            self.traco_pos[i] *= decai_tr
            self.votos[i] *= decai_voto
            self.inib[i] *= decai_inib
            self.refratario[i] = max(0.0, self.refratario[i] - DT)
            if self.refratario[i] > 0.0:
                self.v[i] = 0.0
                continue
            carga = 0.0
            linha = self.pesos[i]
            for j in entrou:
                carga += linha[j]
            # inibicao divisiva: quem foi calado ouve menos, em vez de levar um desconto fixo
            self.v[i] = self.v[i] * decai_v + carga * GANHO * (1.0 - self.inib[i])

        # 3. quem passou do limiar dispara; o mais alto cala os outros (winner-take-all)
        venceu = -1
        melhor = 0.0
        for i in range(self._n_out):
            if self.refratario[i] <= 0.0 and self.v[i] >= self.limiares[i]:
                margem = self.v[i] - self.limiares[i]
                if venceu < 0 or margem > melhor:
                    venceu, melhor = i, margem

        if venceu >= 0:
            self.spikes += 1
            self.traco_pos[venceu] = 1.0
            self.votos[venceu] += 1.0
            self.v[venceu] = 0.0
            self.refratario[venceu] = REFRATARIO
            for i in range(self._n_out):
                if i != venceu:
                    self.inib[i] = _lim(self.inib[i] + INIB_FORCA, 0.0, INIB_MAX)
            # STDP: quem estava ativo no instante do disparo fortalece, quem estava quieto enfraquece
            linha = self.pesos[venceu]
            for j in range(self._n_in):
                desvio = self.traco_pre[j] - self.media_pre[j]
                linha[j] = _lim(linha[j] + ETA_STDP * desvio, W_MIN, W_MAX)
            self._normaliza()

        # 4. homeostase: media de disparo e limiar correndo atras do alvo
        for i in range(self._n_out):
            spike = 1.0 if i == venceu else 0.0
            self.taxas[i] += (spike / DT - self.taxas[i]) * decai_taxa
            self.limiares[i] = _lim(
                self.limiares[i] + ETA_LIMIAR * (self.taxas[i] - TAXA_ALVO) * DT * 100.0,
                LIMIAR_MIN, LIMIAR_MAX)

    # ---------- o que o painel pergunta ----------

    def escolher(self):
        """Comportamento vigente e por quanto tempo, pra quando o painel pedir o proximo."""
        with self._trava:
            i, conf = self._vencedor()
            lo, hi = COMPORTAMENTOS[self.nomes[i]]
            return {"comportamento": self.nomes[i],
                    "duracao": round(lo + (hi - lo) * conf, 2),
                    "confianca": round(conf, 3)}

    def _relativos(self):
        """Surpresa de cada neuronio: quanto ele dispara AGORA acima do proprio normal.

        Contagem bruta de spike nao serve, porque os neuronios acabam com taxas e limiares bem
        diferentes (e com a homeostase lenta, de proposito): o mais barulhento venceria em
        qualquer situacao. Dividir pela taxa tambem nao serve -- com piso constante, um spike
        solto de um neuronio quieto vale mais que a empolgacao real de um neuronio ativo.

        Entao e desvio em unidades de ruido (z de Poisson): 0 = disparando como de costume,
        ~1 = podia ser acaso, >2 = esta mesmo empolgado com o que esta acontecendo.
        """
        z = []
        for k in range(self._n_out):
            esperado = self.taxas[k] * TAU_VOTO
            z.append((self.votos[k] - esperado) / math.sqrt(esperado + 1.0))
        return z

    def _vencedor(self):
        if sum(self.votos) <= 1e-9:  # ninguem disparou ainda: quem esta mais perto de disparar
            i = max(range(self._n_out), key=lambda k: self.v[k] - self.limiares[k])
            return i, 0.0
        rel = self._relativos()
        i = max(range(self._n_out), key=lambda k: rel[k])
        ordem = sorted(rel, reverse=True)
        # Confianca: distancia do 2o colocado em unidades de ruido, amansada. Cortar em 2 sigma
        # saturava em 1.0 quase sempre, e aí toda duracao saía no maximo da faixa (90 s dormindo).
        margem = max(0.0, ordem[0] - ordem[1])
        return i, margem / (margem + 2.0)

    def esquecer(self):
        """Comeca de novo: pesos sorteados, limiares em 1, idade zero."""
        with self._trava:
            self._zera()
            self._grava()
        return self.state

    def set_modo(self, modo):
        self.modo = "instinto" if modo == "instinto" else "cerebro"
        with self._trava:
            self._grava()
        return self.modo

    # ---------- thread, publicacao e disco ----------

    def _loop(self):
        proximo = time.monotonic()
        tick = 0
        ultimo_save = time.monotonic()
        while True:
            proximo += DT
            dorme = proximo - time.monotonic()
            if dorme > 0:
                time.sleep(dorme)
            else:
                proximo = time.monotonic()  # atrasou (maquina ocupada): nao acumula divida
            tick += 1
            try:
                stats, extra = self.fonte()
                with self._trava:
                    self.passo(stats, extra)
                    if tick % PUBLICA_CADA == 0:
                        self._publica()
                    if time.monotonic() - ultimo_save > SALVA_CADA:
                        ultimo_save = time.monotonic()
                        self._grava()
            except Exception as exc:  # nunca derrubar a thread
                self.state = {**self.state, "erro": str(exc)}

    def _publica(self):
        i, conf = self._vencedor()
        rel = self._relativos()
        lo, hi = COMPORTAMENTOS[self.nomes[i]]
        self.state = {
            "modo": self.modo,
            "comportamento": self.nomes[i],
            "duracao": round(lo + (hi - lo) * conf, 2),
            "confianca": round(conf, 3),
            "idade": round(self.idade, 1),
            "spikes": self.spikes,
            "neuronios": [{"nome": n, "taxa": round(self.taxas[k], 2),
                           "limiar": round(self.limiares[k], 2),
                           "carga": round(_lim(self.v[k] / max(self.limiares[k], 1e-6)), 3),
                           "voto": round(self.votos[k], 2),
                           # quanto o vencedor da vez calou este -- o painel desenha quem esta mudo
                           "inib": round(self.inib[k], 3),
                           "relativo": round(rel[k], 2)}
                          for k, n in enumerate(self.nomes)],
            "sensores": [{"nome": n, "rotulo": SENSORES[n],
                          "valor": round(_lim(self.sensores.valores.get(n, 0.0)), 3),
                          "taxa": round(self.taxas_in[k], 1)}
                         for k, n in enumerate(SENSORES)],
            "pesos": [[round(w, 3) for w in linha] for linha in self.pesos],
        }

    def _carrega(self):
        try:
            d = json.loads(CEREBRO.read_text())
        except Exception:
            return
        pesos = d.get("pesos")
        if (isinstance(pesos, list) and len(pesos) == self._n_out
                and all(isinstance(l, list) and len(l) == self._n_in for l in pesos)):
            self.pesos = [[_lim(float(w), W_MIN, W_MAX) for w in linha] for linha in pesos]
            self._normaliza()
        lim = d.get("limiares")
        if isinstance(lim, list) and len(lim) == self._n_out:
            self.limiares = [_lim(float(x), LIMIAR_MIN, LIMIAR_MAX) for x in lim]
        mp = d.get("media_pre")
        if isinstance(mp, list) and len(mp) == self._n_in:
            self.media_pre = [_lim(float(x)) for x in mp]
        taxas = d.get("taxas")
        if isinstance(taxas, list) and len(taxas) == self._n_out:
            self.taxas = [float(x) for x in taxas]
        self.idade = float(d.get("idade") or 0.0)
        self.spikes = int(d.get("spikes") or 0)
        if d.get("modo") in ("cerebro", "instinto"):
            self.modo = d["modo"]

    def _grava(self):
        try:
            CEREBRO.parent.mkdir(parents=True, exist_ok=True)
            tmp = CEREBRO.with_suffix(".tmp")
            tmp.write_text(json.dumps({
                "modo": self.modo,
                "idade": round(self.idade, 1),
                "spikes": self.spikes,
                "pesos": [[round(w, 4) for w in linha] for linha in self.pesos],
                "limiares": [round(x, 4) for x in self.limiares],
                "media_pre": [round(x, 4) for x in self.media_pre],
                "taxas": [round(x, 4) for x in self.taxas],
                "sensores": list(SENSORES),
                "comportamentos": self.nomes,
            }))
            tmp.replace(CEREBRO)
        except Exception:
            pass


if __name__ == "__main__":
    # Teste solto, sem subir o painel: quatro situacoes distintas se alternando. O que se quer ver
    # e CADA situacao puxando um comportamento diferente e estavel -- se todas puxarem o mesmo, ou
    # se o comportamento mudar a esmo dentro da mesma situacao, a rede nao esta selecionando nada.
    import sys
    from collections import Counter

    minutos = float(sys.argv[1]) if len(sys.argv) > 1 else 10.0
    if len(sys.argv) > 2:  # acelera so o aprendizado, pra ver em minutos o que leva horas
        globals()["ETA_STDP"] = ETA_STDP * float(sys.argv[2])
        globals()["ETA_LIMIAR"] = ETA_LIMIAR * float(sys.argv[2])
    SITUACOES = {
        "jogo":     {"cpu": 0.9, "gpu": 0.95, "calor": 0.8, "mem": 0.6, "volume": 0.7},
        "musica":   {"musica": 1.0, "volume": 0.9, "cpu": 0.2, "troca_musica": 0.3},
        "download": {"rede": 0.95, "disco": 0.8, "cpu": 0.3, "pico_rede": 0.4},
        "ocioso":   {"cpu": 0.05, "gpu": 0.05, "noite": 0.9},
    }
    DURA = 20.0  # segundos por situacao

    t = Texugo.__new__(Texugo)
    t.fonte, t.nomes, t.sensores = (lambda: ({}, {})), list(COMPORTAMENTOS), Sensores()
    t.modo, t.state, t._trava = "cerebro", {}, threading.Lock()
    t._n_in, t._n_out = len(SENSORES), len(COMPORTAMENTOS)
    t._zera()

    hist = {k: Counter() for k in SITUACOES}
    nomes_sit = list(SITUACOES)
    passos = int(minutos * 60 / DT)
    for n in range(passos):
        fase = n * DT
        sit = nomes_sit[int(fase / DURA) % len(nomes_sit)]
        base = SITUACOES[sit]
        for k in SENSORES:
            alvo = base.get(k, 0.0)
            if k not in FASICOS:
                t.sensores.valores[k] = alvo + random.gauss(0, 0.04)
            elif alvo and random.random() < alvo * DT * 4:
                t.sensores.valores[k] = 1.0
        t.passo(None, None)
        if fase > minutos * 60 * 0.6:  # so a segunda metade conta: a primeira e aprendizado
            hist[sit][t.nomes[t._vencedor()[0]]] += 1

    print(f"{minutos:.0f} min simulados. Comportamento escolhido em cada situacao (so o 2o tempo):\n")
    for sit, c in hist.items():
        tot = sum(c.values()) or 1
        linha = "  ".join(f"{k} {100*v//tot}%" for k, v in c.most_common(3))
        print(f"  {sit:9s} -> {linha}")
    print("\ntaxas  =", [round(x, 2) for x in t.taxas])
    print("limiares=", [round(x, 2) for x in t.limiares])
    print("\npesos (linha = comportamento, coluna = sensor):")
    print("        " + " ".join(f"{n[:5]:>5s}" for n in SENSORES))
    for k, n in enumerate(t.nomes):
        print(f"{n:7s} " + " ".join(f"{w:5.2f}" for w in t.pesos[k]))
