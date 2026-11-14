"""Genera el grafo del AFD (Graphviz) directamente desde TABLA, para que siempre coincida
con la matriz de la Fase 1. python afd_dot.py > afd.dot y luego dot -Tpng afd.dot -o afd.png"""
from lexer import TABLA, ACEPTACION

aristas = {}
for q, fila in TABLA.items():
    for col, destino in fila.items():
        aristas.setdefault((q, destino), []).append(col)

print('digraph AFD {\n  rankdir=LR; node [shape=circle, fontname="Helvetica"];')
print('  inicio [shape=point]; inicio -> q0;')
for q in TABLA:
    forma = 'doublecircle' if q in ACEPTACION else 'circle'
    token = ' \\n%s' % ACEPTACION[q] if q in ACEPTACION else ''
    print('  q%d [shape=%s, label="q%d%s"];' % (q, forma, q, token))

for (o, d), cols in sorted(aristas.items()):
    etiqueta = ', '.join(c.replace('\n', '\\\\n').replace('"', '\\"') for c in cols)
    if len(cols) > 4:
        etiqueta = 'casi todo'
    print('  q%d -> q%d [label="%s"];' % (o, d, etiqueta))
print('}')
