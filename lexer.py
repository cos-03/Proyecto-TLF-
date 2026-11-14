"""Analizador léxico dirigido por tabla: implementa el AFD de la Fase 1.

ALFABETO = Σ (sección 1.1)
clase_de = agrupa cada símbolo de Σ en una columna de la matriz
TABLA = matriz de transiciones δ (sección 1.5); lo que no aparece va a qE
ACEPTACION = F, con el token que reconoce cada estado de aceptación
"""
from collections import namedtuple

# ---------------------------------------------------------------- Σ
LETRAS = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
DIGITOS = set("0123456789")
SIMBOLOS = set('_."+-*/=!<>(){};#')
BLANCOS = set(" \t\r\n")
OTROS = set("$%&',:?@[\\]^`|~")
ESPANOL = set("áéíóúÁÉÍÓÚñÑüÜ¡¿")
ALFABETO = LETRAS | DIGITOS | SIMBOLOS | BLANCOS | OTROS | ESPANOL

COLUMNAS = ['letra', 'digito', '_', '.', '"', '+', '-', '*', '/', '=', '!',
            '<', '>', '(', ')', '{', '}', ';', '#', 'esp', '\n', 'otro']

def clase_de(c):
    """Columna de la matriz a la que pertenece el símbolo c (None si c no está en Σ)."""
    if c in LETRAS:
        return 'letra'
    if c in DIGITOS:
        return 'digito'
    if c in SIMBOLOS:
        return c
    if c == '\n':
        return '\n'
    if c in ' \t\r':
        return 'esp'
    if c in OTROS or c in ESPANOL:
        return 'otro'
    return None

# ---------------------------------------------------------------- δ
SUMIDERO = -1 # qE
TABLA = {
    0: {'letra': 1, 'digito': 2, '"': 5, '+': 7, '-': 8, '*': 9, '/': 10,
        '=': 11, '!': 13, '<': 15, '>': 17, '(': 19, ')': 20, '{': 21,
        '}': 22, ';': 23, '#': 24, 'esp': 25, '\n': 25},
    1: {'letra': 1, 'digito': 1, '_': 1},
    2: {'digito': 2, '.': 3},
    3: {'digito': 4},
    4: {'digito': 4},
    5: dict({c: 5 for c in COLUMNAS if c not in ('"', '\n')}, **{'"': 6}),
    6: {}, 7: {}, 8: {}, 9: {}, 10: {},
    11: {'=': 12},
    12: {},
    13: {'=': 14},
    14: {},
    15: {'=': 16},
    16: {},
    17: {'=': 18},
    18: {},
    19: {}, 20: {}, 21: {}, 22: {}, 23: {},
    24: {c: 24 for c in COLUMNAS if c != '\n'},
    25: {'esp': 25, '\n': 25},
}

ACEPTACION = {
    1: 'ID', 2: 'NUM', 4: 'NUM', 6: 'CADENA',
    7: 'MAS', 8: 'MENOS', 9: 'POR', 10: 'DIV',
    11: 'ASIG', 12: 'IGUAL', 14: 'DIF',
    15: 'MENOR', 16: 'MENORIG', 17: 'MAYOR', 18: 'MAYORIG',
    19: 'PAR_A', 20: 'PAR_C', 21: 'LLAVE_A', 22: 'LLAVE_C', 23: 'PYC',
    24: 'COMENTARIO', 25: 'ESPACIO',
}

DESCARTADOS = {'COMENTARIO', 'ESPACIO'}
RESERVADAS = {
    'programa': 'PROGRAMA', 'var': 'VAR', 'si': 'SI', 'sino': 'SINO',
    'mientras': 'MIENTRAS', 'regar': 'REGAR', 'mostrar': 'MOSTRAR',
    'alerta': 'ALERTA'
}

Token = namedtuple('Token', 'tipo lexema lin col camino')
Diagnostico = namedtuple('Diagnostico', 'clase lin col mensaje')

class Lexer:
    def __init__(self, texto):
        self.texto = texto
        self.tokens = []
        self.errores = []
        self.fin = (1, 1) # línea y columna donde termina el archivo

    def analizar(self):
        texto, n = self.texto, len(self.texto)
        pos, lin, col = 0, 1, 1
        while pos < n:
            estado, i, camino, ultimo = 0, pos, [0], None
            # recorre δ y recuerda el último estado de aceptación (más largo)
            while i < n:
                cl = clase_de(texto[i])
                if cl is None:
                    break
                sig = TABLA[estado].get(cl, SUMIDERO)
                if sig == SUMIDERO:
                    break
                estado, i = sig, i + 1
                camino.append(estado)
                if estado in ACEPTACION:
                    ultimo = (estado, i, len(camino))
            if ultimo:
                est, fin, k = ultimo
                lexema = texto[pos:fin]
                tipo = ACEPTACION[est]
                if tipo == 'ID':
                    tipo = RESERVADAS.get(lexema, 'ID')
                if tipo not in DESCARTADOS:
                    self.tokens.append(Token(tipo, lexema, lin, col, camino[:k]))
            else:
                fin = self._error(estado, pos, i, lin, col)
            for ch in texto[pos:fin]:
                lin, col = (lin + 1, 1) if ch == '\n' else (lin, col + 1)
            pos = fin
        self.fin = (lin, col)
        return self.tokens, self.errores

    def _error(self, estado, pos, i, lin, col):
        """Registra el error según el estado donde murió el AFD; devuelve dónde seguir."""
        texto = self.texto
        car = texto[i] if i < len(texto) else None
        if estado == 0:
            fin = pos + 1
            if clase_de(texto[pos]) is None:
                msg = 'el símbolo no pertenece al alfabeto Σ'
            else:
                msg = 'el símbolo no puede iniciar ningún token'
        elif estado == 5: # cadena sin cerrar
            fin = texto.find('\n', pos)
            fin = len(texto) if fin == -1 else fin
            if car is not None and car != '\n':
                msg = 'símbolo fuera del alfabeto Σ dentro de una cadena'
            else:
                msg = 'cadena sin cerrar: falta la comilla \'"\' antes del fin de línea'
        elif estado == 13: # ! aislado
            fin = pos + 1
            msg = "el símbolo '!' solo es válido en el operador '!='"
        else:
            fin = max(i, pos + 1)
            msg = 'lexema inválido'
        self.errores.append(Diagnostico('Léxico', lin, col,
                                       '%s (lexema %r)' % (msg, texto[pos:fin].rstrip('\r'))))
        return fin
