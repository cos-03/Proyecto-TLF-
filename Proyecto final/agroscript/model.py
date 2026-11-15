"""Modelos compartidos por el lexer y el parser."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class TokenKind(str, Enum):
    """Clases de tokens que reconoce el lenguaje AgroScript.

    Cada valor es el nombre simbólico usado en los reportes del lexer.
    """

    PROGRAM = "PROGRAMA"
    VAR = "VAR"
    IF = "SI"
    ELSE = "SINO"
    WHILE = "MIENTRAS"
    WATER = "REGAR"
    SHOW = "MOSTRAR"
    ALERT = "ALERTA"
    ID = "ID"
    NUMBER = "NUM"
    STRING = "CADENA"
    PLUS = "MAS"
    MINUS = "MENOS"
    STAR = "POR"
    SLASH = "DIV"
    ASSIGN = "ASIG"
    EQUAL = "IGUAL"
    NOT_EQUAL = "DIF"
    LESS = "MENOR"
    LESS_EQUAL = "MENORIG"
    GREATER = "MAYOR"
    GREATER_EQUAL = "MAYORIG"
    LEFT_PAREN = "PAR_A"
    RIGHT_PAREN = "PAR_C"
    LEFT_BRACE = "LLAVE_A"
    RIGHT_BRACE = "LLAVE_C"
    SEMICOLON = "PYC"
    EOF = "EOF"


@dataclass(frozen=True)
class Token:
    """Token reconocido, con su lexema, posición y recorrido por el AFD.

    Attributes:
        kind: Categoría del token.
        lexeme: Texto exacto del código fuente que produjo el token.
        value: Valor normalizado, si el lexer lo define; de lo contrario, ``None``.
        line: Línea del primer carácter del lexema, comenzando en 1.
        column: Columna del primer carácter del lexema, comenzando en 1.
        states: Estados del AFD recorridos al reconocer el lexema.
    """

    kind: TokenKind
    lexeme: str
    value: str | None
    line: int
    column: int
    states: tuple[str, ...]


@dataclass(frozen=True)
class LexicalError:
    """Error léxico con el fragmento problemático y su ubicación.

    Attributes:
        message: Descripción del error detectado por el lexer.
        lexeme: Fragmento de código fuente que no pudo reconocerse.
        line: Línea donde comienza el fragmento, comenzando en 1.
        column: Columna donde comienza el fragmento, comenzando en 1.
        state: Estado del AFD en el que se detectó el error.
    """

    message: str
    lexeme: str
    line: int
    column: int
    state: str


@dataclass
class LexResult:
    """Resultado del análisis léxico.

    Attributes:
        tokens: Tokens reconocidos en orden, incluido EOF si corresponde.
        errors: Errores léxicos encontrados durante el recorrido del código.
    """

    tokens: list[Token]
    errors: list[LexicalError]


@dataclass
class ParseNode:
    """Nodo del árbol de derivación sintáctica.

    Attributes:
        label: Símbolo gramatical o lexema representado por el nodo.
        children: Nodos derivados de este símbolo, en orden de aparición.
    """

    label: str
    children: list[ParseNode] = field(default_factory=list)


@dataclass(frozen=True)
class SyntaxErrorInfo:
    """Error sintáctico reportado por el parser.

    Attributes:
        message: Descripción de lo esperado y de lo encontrado.
        line: Línea del token que provocó el error, comenzando en 1.
        column: Columna del token que provocó el error, comenzando en 1.
    """

    message: str
    line: int
    column: int

