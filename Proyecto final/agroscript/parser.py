"""Parser descendente recursivo basado en la gramática G2 LL(1)."""

from __future__ import annotations

from .model import ParseNode, SyntaxErrorInfo, Token, TokenKind


_STATEMENT_STARTS = frozenset({
    TokenKind.VAR, TokenKind.ID, TokenKind.IF, TokenKind.WHILE,
    TokenKind.WATER, TokenKind.SHOW, TokenKind.ALERT,
})
_RELATIONAL = frozenset({
    TokenKind.EQUAL, TokenKind.NOT_EQUAL, TokenKind.LESS,
    TokenKind.LESS_EQUAL, TokenKind.GREATER, TokenKind.GREATER_EQUAL,
})
_EXPR_FOLLOW = _RELATIONAL | frozenset({
    TokenKind.SEMICOLON, TokenKind.RIGHT_PAREN,
})
_TERM_FOLLOW = _EXPR_FOLLOW | frozenset({TokenKind.PLUS, TokenKind.MINUS})


class _ParseFailure(Exception):
    def __init__(self, error: SyntaxErrorInfo) -> None:
        super().__init__(error.message)
        self.error = error


class Parser:
    """Analiza tokens y devuelve un árbol más los errores sintácticos."""

    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.current = 0
        self.errors: list[SyntaxErrorInfo] = []

    def parse(self) -> tuple[ParseNode | None, list[SyntaxErrorInfo]]:
        try:
            root = self._programa()
        except _ParseFailure as failure:
            self.errors.append(failure.error)
            root = None
        return root, self.errors

    def _programa(self) -> ParseNode:
        children = [
            self._expect(TokenKind.PROGRAM, "'programa'"),
            self._expect(TokenKind.ID, "un identificador"),
            self._expect(TokenKind.LEFT_BRACE, "'{'"),
            self._sentencias(),
            self._expect(TokenKind.RIGHT_BRACE, "'}'"),
            self._expect(TokenKind.EOF, "fin de archivo"),
        ]
        return ParseNode("<programa>", children)

    def _sentencias(self) -> ParseNode:
        if self._kind() in {TokenKind.RIGHT_BRACE, TokenKind.EOF}:
            return ParseNode("<sentencias>", [ParseNode("ε")])

        start = self.current
        try:
            sentence = self._sentencia()
        except _ParseFailure as failure:
            self.errors.append(failure.error)
            self._synchronize(start, failure.error)
            return self._sentencias()
        return ParseNode("<sentencias>", [sentence, self._sentencias()])

    def _sentencia(self) -> ParseNode:
        kind = self._kind()
        if kind == TokenKind.VAR:
            child = self._declaracion()
        elif kind == TokenKind.ID:
            child = self._asignacion()
        elif kind == TokenKind.IF:
            child = self._condicional()
        elif kind == TokenKind.WHILE:
            child = self._ciclo()
        elif kind in {TokenKind.WATER, TokenKind.SHOW, TokenKind.ALERT}:
            child = self._accion()
        else:
            self._fail(
                "se esperaba una sentencia (var, ID, si, mientras, regar, mostrar o alerta)"
            )
        return ParseNode("<sentencia>", [child])

    def _declaracion(self) -> ParseNode:
        return ParseNode("<declaracion>", [
            self._expect(TokenKind.VAR, "'var'"),
            self._expect(TokenKind.ID, "un identificador"),
            self._expect(TokenKind.ASSIGN, "'='"),
            self._expr(),
            self._expect(TokenKind.SEMICOLON, "';'"),
        ])

    def _asignacion(self) -> ParseNode:
        return ParseNode("<asignacion>", [
            self._expect(TokenKind.ID, "un identificador"),
            self._expect(TokenKind.ASSIGN, "'='"),
            self._expr(),
            self._expect(TokenKind.SEMICOLON, "';'"),
        ])

    def _condicional(self) -> ParseNode:
        return ParseNode("<condicional>", [
            self._expect(TokenKind.IF, "'si'"),
            self._expect(TokenKind.LEFT_PAREN, "'('"),
            self._condicion(),
            self._expect(TokenKind.RIGHT_PAREN, "')'"),
            self._bloque(),
            self._sino_opt(),
        ])

    def _sino_opt(self) -> ParseNode:
        if self._kind() == TokenKind.ELSE:
            return ParseNode("<sino_opt>", [
                self._expect(TokenKind.ELSE, "'sino'"),
                self._bloque(),
            ])
        return ParseNode("<sino_opt>", [ParseNode("ε")])

    def _ciclo(self) -> ParseNode:
        return ParseNode("<ciclo>", [
            self._expect(TokenKind.WHILE, "'mientras'"),
            self._expect(TokenKind.LEFT_PAREN, "'('"),
            self._condicion(),
            self._expect(TokenKind.RIGHT_PAREN, "')'"),
            self._bloque(),
        ])

    def _accion(self) -> ParseNode:
        kind = self._kind()
        if kind == TokenKind.WATER:
            name, symbol = "'regar'", TokenKind.WATER
        elif kind == TokenKind.SHOW:
            name, symbol = "'mostrar'", TokenKind.SHOW
        elif kind == TokenKind.ALERT:
            name, symbol = "'alerta'", TokenKind.ALERT
        else:
            self._fail("se esperaba una acción")
        keyword = self._expect(symbol, name)
        opening = self._expect(TokenKind.LEFT_PAREN, "'('")
        if kind == TokenKind.ALERT:
            argument = self._expect(TokenKind.STRING, "una cadena")
        else:
            argument = self._expr()
        return ParseNode("<accion>", [
            keyword,
            opening,
            argument,
            self._expect(TokenKind.RIGHT_PAREN, "')'"),
            self._expect(TokenKind.SEMICOLON, "';'"),
        ])

    def _bloque(self) -> ParseNode:
        return ParseNode("<bloque>", [
            self._expect(TokenKind.LEFT_BRACE, "'{'"),
            self._sentencias(),
            self._expect(TokenKind.RIGHT_BRACE, "'}'"),
        ])

    def _condicion(self) -> ParseNode:
        return ParseNode("<condicion>", [
            self._expr(),
            self._oprel(),
            self._expr(),
        ])

    def _oprel(self) -> ParseNode:
        if self._kind() not in _RELATIONAL:
            self._fail("se esperaba un operador relacional (==, !=, <, <=, >, >=)")
        return ParseNode("<oprel>", [self._terminal(self._advance())])

    def _expr(self) -> ParseNode:
        return ParseNode("<expr>", [self._termino(), self._expr_prima()])

    def _expr_prima(self) -> ParseNode:
        kind = self._kind()
        if kind in {TokenKind.PLUS, TokenKind.MINUS}:
            operator = self._terminal(self._advance())
            return ParseNode("<expr'>", [operator, self._termino(), self._expr_prima()])
        if kind in _EXPR_FOLLOW or kind in _STATEMENT_STARTS:
            return ParseNode("<expr'>", [ParseNode("ε")])
        self._fail("se esperaba '+', '-', un operador relacional, ')' o ';'")

    def _termino(self) -> ParseNode:
        return ParseNode("<termino>", [self._factor(), self._termino_prima()])

    def _termino_prima(self) -> ParseNode:
        kind = self._kind()
        if kind in {TokenKind.STAR, TokenKind.SLASH}:
            operator = self._terminal(self._advance())
            return ParseNode("<termino'>", [operator, self._factor(), self._termino_prima()])
        if kind in _TERM_FOLLOW or kind in _STATEMENT_STARTS:
            return ParseNode("<termino'>", [ParseNode("ε")])
        self._fail("se esperaba '*', '/', '+', '-', un comparador, ')' o ';'")

    def _factor(self) -> ParseNode:
        kind = self._kind()
        if kind == TokenKind.MINUS:
            return ParseNode("<factor>", [
                self._terminal(self._advance()), self._factor(),
            ])
        if kind == TokenKind.LEFT_PAREN:
            return ParseNode("<factor>", [
                self._terminal(self._advance()),
                self._expr(),
                self._expect(TokenKind.RIGHT_PAREN, "')'"),
            ])
        if kind in {TokenKind.ID, TokenKind.NUMBER}:
            return ParseNode("<factor>", [self._terminal(self._advance())])
        self._fail("se esperaba un número, un identificador, '(' o '-'")

    def _expect(self, kind: TokenKind, expected: str) -> ParseNode:
        if self._kind() != kind:
            self._fail(f"se esperaba {expected}, pero se encontró {self._found()}")
        return self._terminal(self._advance())

    def _terminal(self, token: Token) -> ParseNode:
        return ParseNode(f"{token.kind.value} {token.lexeme!r}")

    def _synchronize(self, start: int, error: SyntaxErrorInfo) -> None:
        if (
            error.message.startswith("se esperaba ';'")
            and self._kind() in _STATEMENT_STARTS
        ):
            return
        if self.current == start and self._kind() not in {
            TokenKind.RIGHT_BRACE, TokenKind.EOF,
        }:
            self._advance()

        nested_braces = 0
        while self._kind() != TokenKind.EOF:
            kind = self._kind()
            if nested_braces == 0:
                if kind == TokenKind.SEMICOLON:
                    self._advance()
                    return
                if kind == TokenKind.RIGHT_BRACE or kind in _STATEMENT_STARTS:
                    if kind == TokenKind.RIGHT_BRACE:
                        return
                    if self.tokens[self.current].line > error.line:
                        return
            if kind == TokenKind.LEFT_BRACE:
                nested_braces += 1
            elif kind == TokenKind.RIGHT_BRACE:
                if nested_braces == 0:
                    return
                nested_braces -= 1
                self._advance()
                if nested_braces == 0:
                    return
                continue
            self._advance()

    def _kind(self) -> TokenKind:
        return self.tokens[self.current].kind

    def _found(self) -> str:
        token = self.tokens[self.current]
        return "fin de archivo" if token.kind == TokenKind.EOF else repr(token.lexeme)

    def _fail(self, message: str) -> None:
        token = self.tokens[self.current]
        raise _ParseFailure(SyntaxErrorInfo(message, token.line, token.column))

    def _advance(self) -> Token:
        token = self.tokens[self.current]
        if token.kind != TokenKind.EOF:
            self.current += 1
        return token


def parse(tokens: list[Token]) -> tuple[ParseNode | None, list[SyntaxErrorInfo]]:
    return Parser(tokens).parse()
