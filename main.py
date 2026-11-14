"""AgroScript: analizador léxico y sintáctico.

Uso:
    python main.py programa.agro                   árbol de derivación o lista de errores
    python main.py programa.agro --tokens          además, cada token con su recorrido en el AFD
    python main.py programa.agro --matriz          imprime la matriz δ (la misma de la Fase 1)
    python main.py programa.agro --html out.html   reporte visual para mostrar en clase

Códigos de salida: 0 = correcto, 1 = hay errores léxicos o sintácticos, 2 = no se pudo leer.
"""
import argparse
import sys
from lexer import Lexer, TABLA, COLUMNAS
from parser import Parser
from visual import generar_html

def imprimir_matriz():
    cols = COLUMNAS
    print('δ'.ljust(6) + ''.join(repr(c)[1:-1].ljust(7) for c in cols))
    for q in sorted(TABLA):
        fila = ''.join(('q%d' % TABLA[q][c] if c in TABLA[q] else '--').ljust(7) for c in cols)
        print(('→q0' if q == 0 else 'q%d' % q).ljust(6) + fila)
    print('qE'.ljust(6) + '(sumidero: toda celda no listada)')

def main(argv=None):
    ap = argparse.ArgumentParser(description='Analizador de AgroScript')
    ap.add_argument('archivo')
    ap.add_argument('--tokens', action='store_true')
    ap.add_argument('--matriz', action='store_true')
    ap.add_argument('--html', metavar='SALIDA')
    a = ap.parse_args(argv)

    try:
        with open(a.archivo, encoding='utf-8') as f:
            texto = f.read()
    except (OSError, UnicodeDecodeError) as e:
        print("No se pudo leer '%s': %s" % (a.archivo, e), file=sys.stderr)
        return 2

    sys.setrecursionlimit(20000)
    if a.matriz:
        imprimir_matriz()
        print()

    lexer = Lexer(texto)
    tokens, err_lex = lexer.analizar()
    parser = Parser(tokens, lexer.fin)
    arbol, err_sin = parser.analizar()
    errores = sorted(err_lex + err_sin, key=lambda d: (d.lin, d.col))

    if a.tokens:
        print('TOKENS RECONOCIDOS POR EL AFD')
        print('lín:col  token       lexema          camino de estados')
        for t in tokens:
            print('%-8s %-11s %-15r %s' % (
                '%d:%d' % (t.lin, t.col), t.tipo, t.lexema,
                ' -> '.join('q%d' % q for q in t.camino)))
        print()

    if a.html:
        with open(a.html, 'w', encoding='utf-8') as f:
            f.write(generar_html(a.archivo, texto, tokens, errores, arbol))
        print("Reporte visual escrito en '%s'" % a.html)

    if errores:
        print("Se encontraron %d error(es) en '%s':" % (len(errores), a.archivo))
        for d in errores:
            print('[%s] línea %d, columna %d: %s' % (d.clase, d.lin, d.col, d.mensaje))
        return 1

    print('ÁRBOL DE DERIVACIÓN SINTÁCTICA')
    print('\n'.join(arbol.imprimir()))
    return 0

if __name__ == '__main__':
    sys.exit(main())
