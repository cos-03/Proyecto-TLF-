"""Interfaz de línea de comandos para analizar archivos .agro."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .lexer import analyze
from .model import LexicalError, SyntaxErrorInfo
from .parser import parse
from .tree import render_tree


def _arguments(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analizador léxico y sintáctico de AgroScript.")
    parser.add_argument("source", type=Path, help="Ruta del archivo .agro")
    parser.add_argument(
        "--tokens", action="store_true",
        help="Muestra los tokens reconocidos y sus recorridos por el AFD.",
    )
    return parser.parse_args(argv)


def _token_report(tokens) -> str:
    lines = ["TOKENS RECONOCIDOS POR EL AFD"]
    lines.append(f"{'línea:col':<12}{'token':<12}{'lexema':<24}camino de estados")
    for token in tokens:
        if token.lexeme == "":
            continue
        path = " -> ".join(token.states)
        lines.append(
            f"{token.line}:{token.column:<8}{token.kind.value:<12}"
            f"{token.lexeme!r:<24}{path}"
        )
    return "\n".join(lines)


def _print_errors(
    source_path: Path,
    lexical_errors: list[LexicalError],
    syntax_errors: list[SyntaxErrorInfo],
) -> None:
    entries = [
        (error.line, error.column, "Léxico", error.message, error.state)
        for error in lexical_errors
    ] + [
        (error.line, error.column, "Sintáctico", error.message, "")
        for error in syntax_errors
    ]
    entries.sort(key=lambda item: (item[0], item[1]))
    print(f"Se encontraron {len(entries)} error(es) en {str(source_path)!r}:")
    for line, column, category, message, state in entries:
        state_text = f" ({state})" if state else ""
        print(f"  [{category}] línea {line}, columna {column}: {message}{state_text}")


def main(argv: list[str] | None = None) -> int:
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    args = _arguments(argv)
    try:
        source = args.source.read_text(encoding="utf-8")
    except OSError as error:
        print(f"No se pudo leer {args.source}: {error}", file=sys.stderr)
        return 2

    lexed = analyze(source)
    tree, syntax_errors = parse(lexed.tokens)

    if args.tokens:
        print(_token_report(lexed.tokens))

    if lexed.errors or syntax_errors:
        _print_errors(args.source, lexed.errors, syntax_errors)
        return 1

    if tree is None:
        print("Error interno: el parser no produjo un árbol.", file=sys.stderr)
        return 1
    print("ÁRBOL DE DERIVACIÓN SINTÁCTICA")
    print(render_tree(tree))
    return 0
