"""Qual piso de desvio separa gosto aprendido de ruido de nascenca."""
import pathlib
REPO = str(pathlib.Path(__file__).resolve().parent.parent)
AQUI = str(pathlib.Path(__file__).resolve().parent)
import random, sys
sys.path.insert(0, REPO)
sys.path.insert(0, AQUI)
import texugo as T
from mede import novo, desvios

random.seed(3)
N = 500
topos, maxes = [], []
for _ in range(N):
    t = novo()
    d = desvios(t)
    picos = [linha[0][1] for linha in d]
    topos += picos
    maxes.append(max(picos))
topos.sort(); maxes.sort()
q = lambda v, p: v[min(len(v) - 1, int(len(v) * p))]
print(f"{N} nascimentos x {len(topos)//N} comportamentos")
print("  desvio do 1o colocado:    p50 %.3f  p90 %.3f  p99 %.3f  max %.3f"
      % (q(topos,.5), q(topos,.9), q(topos,.99), topos[-1]))
print("  pior dos 6 por nascimento: p50 %.3f  p90 %.3f  p99 %.3f  max %.3f"
      % (q(maxes,.5), q(maxes,.9), q(maxes,.99), maxes[-1]))
for piso in (0.13, 0.15, 0.17, 0.18, 0.20, 0.22):
    falsos = sum(1 for x in topos if x >= piso)
    nasc = sum(1 for x in maxes if x >= piso)
    print(f"  piso {piso:.2f}: {100*falsos/len(topos):5.1f}% dos comportamentos inventam gosto; "
          f"{100*nasc/N:5.1f}% dos cerebros novos mostram pelo menos um")
