#!/usr/bin/env bash
# Traz o painel pro que esta no GitHub e reinicia o servico so se precisar.
#   atualizar-painel.sh            atualiza pro main
#   atualizar-painel.sh <ramo>     atualiza pro ramo dado
#   atualizar-painel.sh --voltar   desfaz a ultima atualizacao
#
# O merge pro main e o portao: este script nunca inventa versao, so segue o ramo.
set -u
BASE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$BASE" || exit 1
URL="http://127.0.0.1:8787"
SERVICO=toca-do-texugo.service
ANTERIOR="$HOME/.config/toca-do-texugo/atualizar-anterior"

aviso() { echo "$*"; notify-send "Toca do Texugo" "$*" 2>/dev/null; }

# Reinicia e espera o painel responder de verdade. 1 = nao subiu.
reinicia() {
  systemctl --user restart "$SERVICO" || return 1
  for _ in $(seq 20); do curl -fs -o /dev/null "$URL/api/stats" && return 0; sleep 1; done
  return 1
}

if [[ "${1:-}" == "--voltar" ]]; then
  SHA=$(cat "$ANTERIOR" 2>/dev/null)
  [[ -n "$SHA" ]] || { echo "Não há atualização anterior registrada."; exit 1; }
  git reset --hard --quiet "$SHA" || { echo "Não consegui voltar pro $SHA."; exit 1; }
  reinicia || aviso "Voltei, mas o serviço não respondeu — veja o log."
  echo "Voltou pro $(git log --oneline --no-decorate -1)."
  echo "Atenção: a próxima atualização traz o commit de volta. Conserte no GitHub antes."
  exit 0
fi

RAMO="${1:-main}"

# Mexeu em arquivo e nao commitou? Nao e este script que decide o que fazer com isso.
if [[ -n "$(git status --porcelain)" ]]; then
  echo "Há mudança não commitada aqui — resolva antes de atualizar:"
  git status --short
  exit 1
fi

git fetch --quiet origin "$RAMO" ||
  { aviso "Não consegui buscar origin/$RAMO — rede fora ou o ramo não existe."; exit 1; }
ANTES=$(git rev-parse HEAD) || exit 1
DEPOIS=$(git rev-parse --verify --quiet "origin/$RAMO") || { echo "Não existe origin/$RAMO."; exit 1; }

if [[ "$ANTES" == "$DEPOIS" ]]; then
  echo "Já está em dia ($RAMO · $(git log --oneline --no-decorate -1))."
  exit 0
fi

# So anda em linha reta: divergiu, quem decide e voce -- o script nao faz merge nem rebase.
if ! git merge-base --is-ancestor "$ANTES" "$DEPOIS"; then
  echo "O que está aqui não é ancestral de origin/$RAMO — os dois lados andaram."
  echo "Resolva à mão; este script só avança em linha reta."
  exit 1
fi

echo "Vem aí:"
git log --oneline --no-decorate "$ANTES..$DEPOIS" | sed 's/^/  /'

mkdir -p "$(dirname "$ANTERIOR")" && echo "$ANTES" > "$ANTERIOR"
git merge --ff-only --quiet "origin/$RAMO" || { echo "O merge falhou."; exit 1; }

# `.py` precisa de restart; `index.html` nao -- o painel se recarrega sozinho pelo /api/version
if git diff --name-only "$ANTES" HEAD | grep -q '\.py$'; then
  if reinicia; then
    aviso "Painel atualizado e serviço reiniciado."
  else
    # A parede nao pode ficar quebrada porque um commit nao sobe: volta sozinho
    echo "O serviço não respondeu depois do restart — voltando pro que estava."
    git reset --hard --quiet "$ANTES"
    if reinicia; then
      aviso "Atualização desfeita: o serviço não subiu com a versão nova."
    else
      aviso "Desfiz a atualização e mesmo assim o serviço não responde — veja o log."
    fi
    exit 1
  fi
else
  aviso "Painel atualizado — a página se recarrega sozinha em alguns segundos."
fi
