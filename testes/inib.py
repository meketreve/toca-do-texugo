"""A inibicao lateral diz alguma coisa instante a instante, ou todo mundo vive no teto?"""
import pathlib
REPO = str(pathlib.Path(__file__).resolve().parent.parent)
AQUI = str(pathlib.Path(__file__).resolve().parent)
import random, sys
sys.path.insert(0, REPO)
sys.path.insert(0, AQUI)
import texugo as T
from mede import novo, roda, SITUACOES

random.seed(5)
t = novo()
roda(t, 6, 6)                      # aprende um pouco antes de medir
nomes_sit = list(SITUACOES)
amostras, iguais, venceu_menor = [], 0, 0
n = 0
for passo in range(int(60 / T.DT)):   # 60 s simulados
    sit = SITUACOES[nomes_sit[int(passo * T.DT / 20.0) % 4]]
    for k in T.SENSORES:
        alvo = sit.get(k, 0.0)
        if k not in T.FASICOS:
            t.sensores.valores[k] = alvo + random.gauss(0, 0.04)
        elif alvo and random.random() < alvo * T.DT * 4:
            t.sensores.valores[k] = 1.0
    t.passo(None, None)
    if passo % 50 == 0:               # 2x por segundo, como o painel olharia
        v = list(t.inib)
        amostras.append(v)
        n += 1
        if max(v) - min(v) < 0.05: iguais += 1
        venc = t._vencedor()[0]
        if v[venc] == min(v): venceu_menor += 1
print(f"{n} amostras, INIB_MAX={T.INIB_MAX}, INIB_FORCA={T.INIB_FORCA}, TAU_INIB={T.TAU_INIB}")
col = lambda k: [a[k] for a in amostras]
print("  por neuronio (media):", [round(sum(col(k))/n, 3) for k in range(6)])
espalha = [max(a) - min(a) for a in amostras]
espalha.sort()
print(f"  espalhamento max-min: p50 {espalha[n//2]:.3f}  p90 {espalha[int(n*.9)]:.3f}  max {espalha[-1]:.3f}")
print(f"  amostras em que todos estao praticamente iguais (<0.05): {100*iguais/n:.0f}%")
print(f"  amostras em que o vencedor e o MENOS inibido: {100*venceu_menor/n:.0f}%")
acima = sum(1 for a in amostras for x in a if x > 0.3)
print(f"  neuronios acima de 0.3 (o corte que usei no desenho): {100*acima/(n*6):.0f}%")
