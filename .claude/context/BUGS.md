---
updated: 2026-10-03
tier: 2
---

# Bugs resolvidos

<!-- Arquivo de tier 3 mantido de antes (tier atual: 2). NUNCA importado — grep pela mensagem de erro. -->
<!-- Receita: grep -i "<trecho do erro>" .claude/context/BUGS.md -->

## 2026-10-01 — painel congela na tela, mas a página continua viva

- **Sintoma:** a imagem no monitor virtual para num instante qualquer (relógio parado) e não volta
  mais. Parece a página travada, mas não é: o servidor continua recebendo ~80 requisições/min dela
  e o stream do `/api/audio` segue fluindo a 48 KB/s.
- **Como saber que é isso:** `scrot -a 0,1080,1920,1080 /tmp/p.png` mostra o relógio congelado,
  enquanto `ss -tan '( sport = :8787 )' | grep -c TIME-WAIT` fica em ~80 (a página está pedindo
  `/api/stats` de 1 em 1 s). JS vivo + pixel parado = a composição do Chrome é que parou.
  Nada aparece no `journalctl` nem no `Xorg.0.log`; o renderer não está em laço infinito
  (cuidado: `%CPU` do `ps`/`top` na primeira amostra é média da vida do processo, não o instante).
- **Causa:** a superfície de composição da janela trava. O `requestAnimationFrame` para de ser
  chamado (por isso o mascote e o visualizador congelam), mas os `setInterval` continuam.
  As flags de 0219986 (`--disable-backgrounding-occluded-windows` e cia.) não cobrem este caso:
  elas evitam o *throttling* por janela oculta, não a parada de apresentação.
- **Correção:** forçar a janela a recriar a superfície, sem matar o Chrome (operacional, sem commit):

  ```bash
  W=$(wmctrl -lx | awk '$3 ~ /^[^ ]*toca-do-texugo$/ {print $1; exit}')
  wmctrl -i -r $W -b remove,fullscreen; wmctrl -i -r $W -e 0,0,1080,1920,1080; wmctrl -i -r $W -b add,fullscreen
  ```
