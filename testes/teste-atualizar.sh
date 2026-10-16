#!/usr/bin/env bash
# Bancada do atualizar-painel.sh: remoto falso, clone falso e systemctl/curl falsos.
set -u
SP="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# O lab roda com `cd` pra dentro dele: o caminho do script testado tem de ser absoluto
ALVO="${1:-$SP/../atualizar-painel.sh}"
ALVO="$(cd "$(dirname "$ALVO")" && pwd)/$(basename "$ALVO")"
LAB="$SP/_saida/lab"; rm -rf "$LAB"; mkdir -p "$LAB/bin"
export HOME="$LAB/home"; mkdir -p "$HOME"
export PATH="$LAB/bin:$PATH"

cat > "$LAB/bin/systemctl" <<'X'
#!/usr/bin/env bash
echo "    [systemctl $*]" >&2
[[ "${FALHA_RESTART:-0}" == 1 ]] && exit 1
exit 0
X
cat > "$LAB/bin/curl" <<'X'
#!/usr/bin/env bash
# O painel so responde se o server.py que esta no disco nao for o quebrado
grep -q quebrado "$PAINEL_DIR/server.py" 2>/dev/null && exit 1
exit 0
X
cat > "$LAB/bin/notify-send" <<'X'
#!/usr/bin/env bash
exit 0
X
cat > "$LAB/bin/sleep" <<'X'
#!/usr/bin/env bash
exit 0
X
chmod +x "$LAB/bin/"*

git init -q --bare "$LAB/remoto.git"
git clone -q "$LAB/remoto.git" "$LAB/fonte"
cd "$LAB/fonte"
git config user.email t@t; git config user.name t
echo "<html>v1</html>" > index.html; echo "print(1)" > server.py
cp "$ALVO" atualizar-painel.sh; chmod +x atualizar-painel.sh
git add -A; git commit -qm "inicio"; git push -q origin HEAD:main

git clone -q -b main "$LAB/remoto.git" "$LAB/painel"
PAINEL="$LAB/painel"
export PAINEL_DIR="$PAINEL"
git -C "$PAINEL" config user.email t@t; git -C "$PAINEL" config user.name t

novo_commit() {  # $1 = arquivo, $2 = conteudo, $3 = assunto
  cd "$LAB/fonte"; echo "$2" > "$1"; git add -A; git commit -qm "$3"; git push -q origin HEAD:main
}
caso() { echo; echo "===== $* ====="; }
roda() { cd "$PAINEL"; ./atualizar-painel.sh "$@"; echo "  (saida: $?)"; }

caso "1. ja esta em dia"
roda

caso "2. so o index.html mudou -> sem restart"
novo_commit index.html "<html>v2</html>" "mexe no index"
roda

caso "3. .py mudou -> restart e o servico sobe"
novo_commit server.py "print(2)" "mexe no server"
roda

caso "4. .py mudou e o servico NAO sobe -> volta sozinho"
novo_commit server.py "print(3) # quebrado" "commit ruim"
roda
echo "  HEAD do painel agora: $(cd $PAINEL && git log --oneline --no-decorate -1)"
echo "  conteudo do server.py: $(cat $PAINEL/server.py)"

caso "5. arvore suja -> recusa"
echo "rascunho" >> "$PAINEL/index.html"
roda
cd "$PAINEL" && git checkout -q -- index.html

caso "6. divergiu -> recusa"
cd "$PAINEL" && git commit -q --allow-empty -m "commit local"
roda
cd "$PAINEL" && git reset -q --hard HEAD~1

caso "7. aplica o commit ruim na marra e depois --voltar"
roda
echo "  antes de voltar: $(cd $PAINEL && git log --oneline --no-decorate -1)"
cd "$PAINEL" && ./atualizar-painel.sh --voltar; echo "  (saida: $?)"
echo "  depois de voltar: $(cd $PAINEL && git log --oneline --no-decorate -1)"

caso "8. ramo que nao existe"
roda nao-existe
