"""Analizador sintáctico descendente recursivo para la gramática G2 (LL(1)).
Hay un método por cada no terminal de G2. Cada `if` usa el conjunto de
predicción de la sección 2.7. Devuelve el Árbol de Derivación Sintáctica.
"""
from lexer import Token, Diagnostico

INICIO_SENT = {'VAR', 'ID', 'SI', 'MIENTRAS', 'REGAR', 'MOSTRAR', 'ALERTA'}
# Puntos de sincronización: ID no cuenta, porque también aparece dentro de las expresiones.
SINCRONIZA = {'VAR', 'SI', 'MIENTRAS', 'REGAR', 'MOSTRAR', 'ALERTA'}
OPREL = {'IGUAL': '==', 'DIF': '!=', 'MENOR': '<', 'MENORIG': '<=',
         'MAYOR': '>', 'MAYORIG': '>='}
NOMBRES = {'PROGRAMA': "'programa'", 'ID': 'un identificador', 'LLAVE_A': "'{'",
           'LLAVE_C': "'}'", 'PAR_A': "'('", 'PAR_C': "')'", 'PYC': "';'",
           'ASIG': "'='", 'VAR': "'var'", 'CADENA': 'una cadena entre comillas',
           'EOF': 'fin de archivo'}

class Nodo:
    """Nodo del árbol: no terminal (hijos), terminal (lexema) o ε."""
    def __init__(self, etiqueta, hijos=None, lexema=None):
        self.etiqueta, self.hijos, self.lexema = etiqueta, hijos or [], lexema

    def texto(self):
        return "%s '%s'" % (self.etiqueta, self.lexema) if self.lexema is not None else self.etiqueta

    def imprimir(self, prefijo='', ultimo=True, raiz=True):
        lineas = [self.texto()] if raiz else [prefijo + ('└── ' if ultimo else '├── ') + self.texto()]
        hijo_pref = '' if raiz else prefijo + ('    ' if ultimo else '│   ')
        for k, h in enumerate(self.hijos):
            lineas += h.imprimir(hijo_pref, k == len(self.hijos) - 1, False)
        return lineas

class ErrorSintactico(Exception):
    def __init__(self, token, mensaje):
        super().__init__(mensaje)
        self.token, self.mensaje = token, mensaje

class Parser:
    def __init__(self, tokens, fin):
        self.t = list(tokens) + [Token('EOF', '', fin[0], fin[1], [])]
        self.i = 0
        self.errores = []

    # ---------------------------------------------------------- utilidades
    @property
    def act(self):
        return self.t[self.i]

    def _encontrado(self):
        return 'fin de archivo' if self.act.tipo == 'EOF' else "'%s'" % self.act.lexema

    def _error(self, esperado):
        return ErrorSintactico(self.act, 'se esperaba %s, pero se encontró %s' % (esperado, self._encontrado()))

    def coincidir(self, tipo):
        if self.act.tipo != tipo:
            raise self._error(NOMBRES.get(tipo, tipo))
        tok = self.act
        self.i += 1
        return Nodo(tok.tipo, lexema=tok.lexema)

    # ---------------------------------------------------------- análisis
    def analizar(self):
        try:
            arbol = self.programa()
        except ErrorSintactico as e:
            self.errores.append(self._diag(e))
            arbol = None
        if self.errores:
            arbol = None
        return arbol, self.errores

    @staticmethod
    def _diag(e):
        return Diagnostico('Sintáctico', e.token.lin, e.token.col, e.mensaje)

    def programa(self):
        h = [self.coincidir('PROGRAMA'), self.coincidir('ID'),
             self.coincidir('LLAVE_A'), self.sentencias(),
             self.coincidir('LLAVE_C')]
        if self.act.tipo != 'EOF':
            raise self._error('fin de archivo')
        return Nodo('<programa>', h)

    def sentencias(self):
        """<sentencias> ::= <sentencia> <sentencias> | ε (con recuperación en modo pánico)"""
        nodos = []
        while self.act.tipo not in ('LLAVE_C', 'EOF'):
            inicio = self.i
            try:
                nodos.append(self.sentencia())
            except ErrorSintactico as e:
                self.errores.append(self._diag(e))
                self._sincronizar(inicio)
        nodo = Nodo('<sentencias>', [Nodo('ε')])
        for s in reversed(nodos):
            nodo = Nodo('<sentencias>', [s, nodo])
        return nodo

    def _sincronizar(self, inicio):
        """Descarta tokens hasta después de ';', o hasta '}' / palabra que inicia sentencia.
        Salta completos los bloques { ... } para no generar errores en cascada."""
        while self.act.tipo != 'EOF':
            t = self.act.tipo
            if t == 'PYC':
                self.i += 1
                break
            if t == 'LLAVE_A':
                self._saltar_bloque()
                continue
            if t == 'LLAVE_C' or t in SINCRONIZA:
                break
            self.i += 1
        if self.i == inicio and self.act.tipo != 'EOF':
            self.i += 1 # garantiza progreso

    def _saltar_bloque(self):
        prof = 0
        while self.act.tipo != 'EOF':
            prof += {'LLAVE_A': 1, 'LLAVE_C': -1}.get(self.act.tipo, 0)
            self.i += 1
            if prof == 0:
                break

    def sentencia(self):
        t = self.act.tipo
        if t == 'VAR':
            return Nodo('<sentencia>', [self.declaracion()])
        if t == 'ID':
            return Nodo('<sentencia>', [self.asignacion()])
        if t == 'SI':
            return Nodo('<sentencia>', [self.condicional()])
        if t == 'MIENTRAS':
            return Nodo('<ciclo>', [self.ciclo()]) if False else Nodo('<sentencia>', [self.ciclo()])
        if t in ('REGAR', 'MOSTRAR', 'ALERTA'):
            return Nodo('<sentencia>', [self.accion()])
        raise self._error('una sentencia (var, identificador, si, mientras, regar, mostrar o alerta)')

    def declaracion(self):
        return Nodo('<declaracion>', [self.coincidir('VAR'),
                                      self.coincidir('ID'),
                                      self.coincidir('ASIG'),
                                      self.expr(),
                                      self.coincidir('PYC')])

    def asignacion(self):
        return Nodo('<asignacion>', [self.coincidir('ID'),
                                     self.coincidir('ASIG'),
                                     self.expr(),
                                     self.coincidir('PYC')])

    def condicional(self):
        h = [self.coincidir('SI'), self.coincidir('PAR_A'), self.condicion(),
             self.coincidir('PAR_C'), self.bloque(), self.sino_opt()]
        return Nodo('<condicional>', h)

    def sino_opt(self):
        if self.act.tipo == 'SINO':
            return Nodo('<sino_opt>', [self.coincidir('SINO'), self.bloque()])
        return Nodo('<sino_opt>', [Nodo('ε')])

    def ciclo(self):
        return Nodo('<ciclo>', [self.coincidir('MIENTRAS'),
                                self.coincidir('PAR_A'),
                                self.condicion(),
                                self.coincidir('PAR_C'),
                                self.bloque()])

    def accion(self):
        t = self.act.tipo
        if t in ('REGAR', 'MOSTRAR'):
            h = [self.coincidir(t), self.coincidir('PAR_A'), self.expr(),
                 self.coincidir('PAR_C'), self.coincidir('PYC')]
        else:
            h = [self.coincidir('ALERTA'), self.coincidir('PAR_A'),
                 self.coincidir('CADENA'),
                 self.coincidir('PAR_C'), self.coincidir('PYC')]
        return Nodo('<accion>', h)

    def bloque(self):
        return Nodo('<bloque>', [self.coincidir('LLAVE_A'),
                                 self.sentencias(),
                                 self.coincidir('LLAVE_C')])

    def condicion(self):
        return Nodo('<condicion>', [self.expr(), self.oprel(), self.expr()])

    def oprel(self):
        if self.act.tipo in OPREL:
            return Nodo('<oprel>', [self.coincidir(self.act.tipo)])
        raise self._error('un operador relacional (==, !=, <, <=, >, >=)')

    def expr(self):
        return Nodo('<expr>', [self.termino(), self.expr_prima()])

    def expr_prima(self):
        if self.act.tipo in ('MAS', 'MENOS'):
            return Nodo("<expr'>", [self.coincidir(self.act.tipo),
                                    self.termino(), self.expr_prima()])
        return Nodo("<expr'>", [Nodo('ε')])

    def termino(self):
        return Nodo('<termino>', [self.factor(), self.termino_prima()])

    def termino_prima(self):
        if self.act.tipo in ('POR', 'DIV'):
            return Nodo("<termino'>", [self.coincidir(self.act.tipo),
                                       self.factor(), self.termino_prima()])
        return Nodo("<termino'>", [Nodo('ε')])

    def factor(self):
        t = self.act.tipo
        if t == 'MENOS':
            return Nodo('<factor>', [self.coincidir('MENOS'), self.factor()])
        if t == 'PAR_A':
            return Nodo('<factor>', [self.coincidir('PAR_A'), self.expr(),
                                     self.coincidir('PAR_C')])
        if t in ('ID', 'NUM'):
            return Nodo('<factor>', [self.coincidir(t)])
        raise self._error("un número, un identificador, '(' o '-'")
