"""Mede o desvio de coluna (peso - media dos outros comportamentos no mesmo sensor):
no nascimento (so ruido) e depois de aprender. E o numero que o medidor vai usar."""
import pathlib
REPO = str(pathlib.Path(__file__).resolve().parent.parent)
AQUI = str(pathlib.Path(__file__).resolve().parent)
import random, sys, threading
sys.path.insert(0, REPO)
import texugo as T

SITUACOES = {
    "jogo":     {"cpu": 0.9, "gpu": 0.95, "calor": 0.8, "mem": 0.6, "volume": 0.7},
    "musica":   {"musica": 1.0, "volume": 0.9, "cpu": 0.2, "troca_musica": 0.3},
    "download": {"rede": 0.95, "disco": 0.8, "cpu": 0.3, "pico_rede": 0.4},
    "ocioso":   {"cpu": 0.05, "gpu": 0.05, "noite": 0.9},
}
DURA = 20.0

def novo():
    t = T.Texugo.__new__(T.Texugo)
    t.fonte, t.nomes, t.sensores = (lambda: ({}, {})), list(T.COMPORTAMENTOS), T.Sensores()
    t.modo, t.state, t._trava = "cerebro", {}, threading.Lock()
    t._n_in, t._n_out = len(T.SENSORES), len(T.COMPORTAMENTOS)
    t._zera()
    return t

def desvios(t):
    """Por comportamento: lista de (sensor, peso - media da coluna), ordenada."""
    nomes = list(T.SENSORES)
    out = []
    for i in range(t._n_out):
        linha = []
        for j in range(t._n_in):
            col = [t.pesos[k][j] for k in range(t._n_out)]
            linha.append((nomes[j], t.pesos[i][j] - sum(col) / len(col)))
        linha.sort(key=lambda x: -x[1])
        out.append(linha)
    return out

def roda(t, minutos, acel):
    T.ETA_STDP = 0.004 * acel
    T.ETA_LIMIAR = 0.001 * acel
    nomes_sit = list(SITUACOES)
    for n in range(int(minutos * 60 / T.DT)):
        sit = nomes_sit[int(n * T.DT / DURA) % len(nomes_sit)]
        base = SITUACOES[sit]
        for k in T.SENSORES:
            alvo = base.get(k, 0.0)
            if k not in T.FASICOS:
                t.sensores.valores[k] = alvo + random.gauss(0, 0.04)
            elif alvo and random.random() < alvo * T.DT * 4:
                t.sensores.valores[k] = 1.0
        t.passo(None, None)

if __name__ == "__main__":
    random.seed(7)
    # 1) nascimento: 30 sorteios, so pra ver o tamanho do ruido
    topo_nasc = []
    for _ in range(30):
        for linha in desvios(novo()):
            topo_nasc.append(linha[0][1])
    topo_nasc.sort()
    print("peso medio = %.3f (W_SOMA %.1f / %d sensores)" % (T.W_SOMA/len(T.SENSORES), T.W_SOMA, len(T.SENSORES)))
    print("desvio do 1o colocado AO NASCER: mediana %.3f  p90 %.3f  max %.3f"
          % (topo_nasc[len(topo_nasc)//2], topo_nasc[int(len(topo_nasc)*0.9)], topo_nasc[-1]))

    # 2) depois de aprender
    for mins, acel in ((6, 6), (20, 6)):
        t = novo(); roda(t, mins, acel)
        print("\n--- %d min x%d (= ~%d min de relogio real de aprendizado) spikes=%d ---"
              % (mins, acel, mins*acel, t.spikes))
        for i, linha in enumerate(desvios(t)):
            top = "  ".join("%s %+.3f" % (n, v) for n, v in linha[:3])
            print("  %-7s %s   | pior: %s %+.3f" % (t.nomes[i], top, linha[-1][0], linha[-1][1]))
