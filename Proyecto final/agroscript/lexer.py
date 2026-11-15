"""Analizador léxico de AgroScript implementado con un AFD tabulado."""

from __future__ import annotations

from .model import LexicalError, LexResult, Token, TokenKind


STATES = tuple(f"q{index}" for index in range(26)) + ("qE",)
ACCEPTING = frozenset(
    state for state in STATES
    if state not in {"q0", "q3", "q5", "q13", "qE"}
)
SPANISH = frozenset("áéíóúÁÉÍÓÚñÑüÜ¡¿")
ALPHABET = frozenset(chr(code) for code in range(32, 127)) | frozenset(
    "\t\r\n"
) | SPANISH

CATEGORIES = (
    "LETTER", "DIGIT", "UNDERSCORE", "DOT", "QUOTE", "PLUS", "MINUS",
    "STAR", "SLASH", "EQUAL", "BANG", "LESS", "GREATER", "LEFT_PAREN",
    "RIGHT_PAREN", "LEFT_BRACE", "RIGHT_BRACE", "SEMICOLON", "HASH",
    "SPACE", "NEWLINE", "OTHER",
)


def _new_table() -> dict[str, dict[str, str]]:
    table = {state: {category: "qE" for category in CATEGORIES} for state in STATES}

    def put(state: str, category: str, destination: str) -> None:
        table[state][category] = destination

    put("q0", "LETTER", "q1")
    put("q0", "DIGIT", "q2")
    put("q0", "QUOTE", "q5")
    for category, destination in (
        ("PLUS", "q7"), ("MINUS", "q8"), ("STAR", "q9"), ("SLASH", "q10"),
        ("EQUAL", "q11"), ("BANG", "q13"), ("LESS", "q15"),
        ("GREATER", "q17"), ("LEFT_PAREN", "q19"), ("RIGHT_PAREN", "q20"),
        ("LEFT_BRACE", "q21"), ("RIGHT_BRACE", "q22"),
        ("SEMICOLON", "q23"), ("HASH", "q24"),
        ("SPACE", "q25"), ("NEWLINE", "q25"),
    ):
        put("q0", category, destination)

    for category in ("LETTER", "DIGIT", "UNDERSCORE"):
        put("q1", category, "q1")
    put("q2", "DIGIT", "q2")
    put("q2", "DOT", "q3")
    put("q3", "DIGIT", "q4")
    put("q4", "DIGIT", "q4")

    for category in CATEGORIES:
        if category not in {"QUOTE", "NEWLINE"}:
            put("q5", category, "q5")
    put("q5", "QUOTE", "q6")

    put("q11", "EQUAL", "q12")
    put("q13", "EQUAL", "q14")
    put("q15", "EQUAL", "q16")
    put("q17", "EQUAL", "q18")

    for category in CATEGORIES:
        if category != "NEWLINE":
            put("q24", category, "q24")
    put("q25", "SPACE", "q25")
    put("q25", "NEWLINE", "q25")
    return table


TABLA = _new_table()

_RESERVED = {
    "programa": TokenKind.PROGRAM,
    "var": TokenKind.VAR,
    "si": TokenKind.IF,
    "sino": TokenKind.ELSE,
    "mientras": TokenKind.WHILE,
    "regar": TokenKind.WATER,
    "mostrar": TokenKind.SHOW,
    "alerta": TokenKind.ALERT,
}

_ACCEPTED_TOKENS = {
    "q2": TokenKind.NUMBER,
    "q4": TokenKind.NUMBER,
    "q6": TokenKind.STRING,
    "q7": TokenKind.PLUS,
    "q8": TokenKind.MINUS,
    "q9": TokenKind.STAR,
    "q10": TokenKind.SLASH,
    "q11": TokenKind.ASSIGN,
    "q12": TokenKind.EQUAL,
    "q14": TokenKind.NOT_EQUAL,
    "q15": TokenKind.LESS,
    "q16": TokenKind.LESS_EQUAL,
    "q17": TokenKind.GREATER,
    "q18": TokenKind.GREATER_EQUAL,
    "q19": TokenKind.LEFT_PAREN,
    "q20": TokenKind.RIGHT_PAREN,
    "q21": TokenKind.LEFT_BRACE,
    "q22": TokenKind.RIGHT_BRACE,
    "q23": TokenKind.SEMICOLON,
    "q24": None,
    "q25": None,
}

_SYMBOL_CATEGORIES = {
    "_": "UNDERSCORE",
    ".": "DOT",
    '"': "QUOTE",
    "+": "PLUS",
    "-": "MINUS",
    "*": "STAR",
    "/": "SLASH",
    "=": "EQUAL",
    "!": "BANG",
    "<": "LESS",
    ">": "GREATER",
    "(": "LEFT_PAREN",
    ")": "RIGHT_PAREN",
    "{": "LEFT_BRACE",
    "}": "RIGHT_BRACE",
    ";": "SEMICOLON",
    "#": "HASH",
}


def _classify(character: str) -> str | None:
    if character not in ALPHABET:
        return None
    if "a" <= character <= "z" or "A" <= character <= "Z":
        return "LETTER"
    if "0" <= character <= "9":
        return "DIGIT"
    if character in _SYMBOL_CATEGORIES:
        return _SYMBOL_CATEGORIES[character]
    if character in " \t\r":
        return "SPACE"
    if character == "\n":
        return "NEWLINE"
    return "OTHER"


def _positions(source: str) -> list[tuple[int, int]]:
    result = []
    line, column = 1, 1
    for character in source:
        result.append((line, column))
        if character == "\n":
            line, column = line + 1, 1
        else:
            column += 1
    result.append((line, column))
    return result


class Lexer:
    """Reconoce tokens por coincidencia más larga y conserva su traza AFD."""

    def analyze(self, source: str) -> LexResult:
        tokens: list[Token] = []
        errors: list[LexicalError] = []
        positions = _positions(source)
        index = 0

        while index < len(source):
            start = index
            cursor = start
            state = "q0"
            state_path = [state]
            last_accept: tuple[int, str, tuple[str, ...]] | None = None

            while cursor < len(source):
                category = _classify(source[cursor])
                if category is None:
                    break
                destination = TABLA[state][category]
                if destination == "qE":
                    break
                state = destination
                cursor += 1
                state_path.append(state)
                if state in ACCEPTING:
                    last_accept = (cursor, state, tuple(state_path))

            if last_accept is not None:
                end, accepted_state, accepted_path = last_accept
                lexeme = source[start:end]
                if accepted_state == "q1":
                    kind = _RESERVED.get(lexeme, TokenKind.ID)
                    value: str | float | None = lexeme
                elif accepted_state in {"q2", "q4"}:
                    kind = TokenKind.NUMBER
                    value = lexeme
                elif accepted_state == "q6":
                    kind = TokenKind.STRING
                    value = lexeme[1:-1]
                elif accepted_state == "q24" or accepted_state == "q25":
                    index = end
                    continue
                else:
                    kind = _ACCEPTED_TOKENS[accepted_state]
                    value = lexeme
                tokens.append(
                    Token(kind, lexeme, value, *positions[start], accepted_path)
                )
                index = end
                continue

            line, column = positions[start]
            if state == "q5":
                if cursor < len(source) and _classify(source[cursor]) is None:
                    bad = source[cursor]
                    end = cursor + 1
                    while end < len(source) and source[end] not in '"\n':
                        end += 1
                    if end < len(source) and source[end] == '"':
                        end += 1
                    errors.append(
                        LexicalError(
                            f"el símbolo {bad!r} no pertenece a Σ dentro de la cadena",
                            source[start:end], *positions[cursor], "qE",
                        )
                    )
                    index = end
                else:
                    lexeme = source[start:cursor]
                    errors.append(
                        LexicalError(
                            'cadena sin cerrar: falta la comilla \'"\' antes del fin de línea',
                            lexeme, line, column, "q5",
                        )
                    )
                    index = cursor
                continue
            if state == "q13":
                errors.append(
                    LexicalError(
                        "el símbolo '!' solo es válido en el operador '!='",
                        source[start:start + 1], line, column, "q13",
                    )
                )
                index = start + 1
                continue

            bad = source[start]
            state_name = state if state != "q0" else "q0"
            errors.append(
                LexicalError(
                    f"el símbolo no puede iniciar ningún token (lexema {bad!r})",
                    bad, line, column, state_name,
                )
            )
            index = start + 1

        eof_line, eof_column = positions[len(source)]
        tokens.append(Token(TokenKind.EOF, "", None, eof_line, eof_column, ("q0",)))
        return LexResult(tokens, errors)


def analyze(source: str) -> LexResult:
    return Lexer().analyze(source)
