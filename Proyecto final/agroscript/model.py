"""Modelos compartidos por el lexer y el parser."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class TokenKind(str, Enum):
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
    kind: TokenKind
    lexeme: str
    value: str | None
    line: int
    column: int
    states: tuple[str, ...]


@dataclass(frozen=True)
class LexicalError:
    message: str
    lexeme: str
    line: int
    column: int
    state: str


@dataclass
class LexResult:
    tokens: list[Token]
    errors: list[LexicalError]


@dataclass
class ParseNode:
    label: str
    children: list[ParseNode] = field(default_factory=list)


@dataclass(frozen=True)
class SyntaxErrorInfo:
    message: str
    line: int
    column: int

