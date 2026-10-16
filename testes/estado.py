"""Roda a rede e cospe o /api/texugo de verdade, pro teste do painel nao usar dado inventado."""
import pathlib
REPO = str(pathlib.Path(__file__).resolve().parent.parent)
AQUI = str(pathlib.Path(__file__).resolve().parent)
import json, random, sys, threading
sys.path.insert(0, REPO)
import texugo as T
sys.path.insert(0, AQUI)
from mede import novo, roda

random.seed(11)
minutos = float(sys.argv[1]) if len(sys.argv) > 1 else 0.0
t = novo()
if minutos:
    roda(t, minutos, 6)
t.modo = "cerebro"
t._publica()
print(json.dumps(t.state))
