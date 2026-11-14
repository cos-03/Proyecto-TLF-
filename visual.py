"""Reporte HTML autocontenido: código fuente con errores, tokens con su camino en el AFD
y árbol de derivación plegable. No usa librerías externas."""
from html import escape

def _arbol(n):
    if not n.hijos:
        cls = 'eps' if n.etiqueta == 'ε' else 'term'
        return '<div class="hoja %s">%s</div>' % (cls, escape(n.texto()))
    abierto = ' open' if n.etiqueta in ('<programa>', '<sentencias>', '<sentencia>') else ''
    return '<details%s><summary>%s</summary>%s</details>' % (
        abierto, escape(n.etiqueta), ''.join(_arbol(h) for h in n.hijos))

def generar_html(nombre, texto, tokens, errores, arbol):
    malas = {}
    for d in errores:
        malas.setdefault(d.lin, []).append(d)
    codigo = []
    for i, linea in enumerate(texto.split('\n'), 1):
        cls = ' class="mala"' if i in malas else ''
        codigo.append('<div%s><span class="n">%d</span>%s</div>' % (cls, i, escape(linea) or ' '))
    filas = ''.join(
        '<tr><td>%d:%d</td><td><b>%s</b></td><td><code>%s</code></td><td class="cam">%s</td></tr>'
        % (t.lin, t.col, t.tipo, escape(t.lexema), ' → '.join('q%d' % q for q in t.camino))
        for t in tokens)
    if errores:
        cuerpo = '<h2>Errores (%d)</h2><ul class="err">%s</ul>' % (
            len(errores), ''.join(
                '<li><b>[%s]</b> línea %d, columna %d: %s</li>' % (d.clase, d.lin, d.col, escape(d.mensaje))
                for d in errores))
    else:
        cuerpo = '<h2>Árbol de derivación sintáctica</h2><div class="arbol">%s</div>' % _arbol(arbol)
    estado = ('<span class="mal">%d error(es)</span>' % len(errores)) if errores else '<span class="bien">programa correcto</span>'
    return PLANTILLA % dict(nombre=escape(nombre), estado=estado,
                            codigo=''.join(codigo),
                            cuerpo=cuerpo, ntok=len(tokens), filas=filas)

PLANTILLA = """<!doctype html><html lang="es"><meta charset="utf-8">
<title>AgroScript · %(nombre)s</title>
<style>
:root{--bg:#fafaf7;--fg:#1d2420;--sub:#5d675f;--ln:#d9ddd5;--ac:#2f6b3f;--mal:#b3261e;--cd:#fff}
@media(prefers-color-scheme:dark){:root{--bg:#141815;--fg:#e6ebe4;--sub:#9aa69c;--ln:#2c352e;--ac:#7fc28f;--mal:#ff8a80;--cd:#1b211c}}
body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,sans-serif;padding:24px;max-width:1100px;margin:auto}
h1{font-size:22px;margin:0 0 4px}h2{font-size:17px;margin:4px 0 8px}
.bien{color:var(--ac);font-weight:600}.mal{color:var(--mal);font-weight:600}
section{background:var(--cd);border:1px solid var(--ln);border-radius:10px;padding:12px 16px;margin-top:14px;overflow:auto}
.cod div{font:13px/1.6 ui-monospace,Consolas,monospace;white-space:pre}
.cod .n{display:inline-block;width:2.5em;color:var(--sub);user-select:none}
.cod .mala{background:color-mix(in srgb,var(--mal) 18%%,transparent)}
table{border-collapse:collapse;width:100%%;font-size:13px}td,th{border-bottom:1px solid var(--ln);padding:4px 8px;text-align:left}
.cam{font:12px ui-monospace,monospace;color:var(--sub)}
.arbol{font:13px/1.5 ui-monospace,Consolas,monospace}
.arbol details{margin-left:18px;border-left:1px solid var(--ln);padding-left:8px}
.arbol summary{cursor:pointer;color:var(--ac)}
.hoja{margin-left:26px}.term{font-weight:600}.eps{color:var(--sub)}
.err li{margin:4px 0}
</style>
<h1>AgroScript · %(nombre)s</h1><div>%(estado)s</div>
<section><h2>Código fuente</h2><div class="cod">%(codigo)s</div></section>
<section>%(cuerpo)s</section>
<section><h2>Tokens reconocidos por el AFD (%(ntok)d)</h2>
<table><tr><th>lín:col</th><th>token</th><th>lexema</th><th>camino de estados</th></tr>%(filas)s</table></section>
</html>"""
