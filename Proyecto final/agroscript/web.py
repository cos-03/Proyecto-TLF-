"""Servidor local para la demostración interactiva de AgroScript."""

from __future__ import annotations

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from urllib.parse import urlsplit

from .lexer import analyze
from .model import ParseNode
from .parser import parse
from .tree import render_tree

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_MAX_SOURCE_SIZE = 256 * 1024


def _node_data(node: ParseNode) -> dict[str, object]:
    return {
        "label": node.label,
        "children": [_node_data(child) for child in node.children],
    }


def analyze_source(source: str) -> dict[str, object]:
    lexed = analyze(source)
    tree, syntax_errors = parse(lexed.tokens)
    return {
        "valid": not lexed.errors and not syntax_errors,
        "tokens": [
            {
                "kind": token.kind.value,
                "lexeme": token.lexeme,
                "line": token.line,
                "column": token.column,
                "states": list(token.states),
            }
            for token in lexed.tokens
            if token.kind.value != "EOF"
        ],
        "lexicalErrors": [
            {
                "message": error.message,
                "lexeme": error.lexeme,
                "line": error.line,
                "column": error.column,
                "state": error.state,
            }
            for error in lexed.errors
        ],
        "syntaxErrors": [
            {
                "message": error.message,
                "line": error.line,
                "column": error.column,
            }
            for error in syntax_errors
        ],
        "tree": _node_data(tree) if tree is not None else None,
        "treeText": render_tree(tree) if tree is not None else None,
    }


class _AgroScriptHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, directory=str(_PROJECT_ROOT), **kwargs)

    def do_POST(self) -> None:
        if urlsplit(self.path).path != "/api/analyze":
            self.send_error(404, "Ruta no encontrada")
            return

        try:
            content_length = int(self.headers.get("Content-Length", ""))
        except ValueError:
            self._send_json(400, {"error": "Falta una longitud de contenido válida."})
            return

        if content_length < 0 or content_length > _MAX_SOURCE_SIZE:
            self._send_json(413, {"error": "El programa supera el tamaño máximo permitido."})
            return

        try:
            payload = json.loads(self.rfile.read(content_length))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._send_json(400, {"error": "El cuerpo debe contener JSON válido en UTF-8."})
            return

        if not isinstance(payload, dict) or not isinstance(payload.get("source"), str):
            self._send_json(400, {"error": "Se requiere un campo de texto llamado 'source'."})
            return

        self._send_json(200, analyze_source(payload["source"]))

    def _send_json(self, status: int, payload: dict[str, object]) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)


def run_server() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", 0), _AgroScriptHandler)
    url = f"http://127.0.0.1:{server.server_port}/"
    print(f"Demostración interactiva disponible en {url}")
    try:
        import webbrowser

        if not webbrowser.open(url):
            print("No se abrió el navegador automáticamente; usa la URL anterior.")
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor AgroScript detenido.")
    finally:
        server.server_close()
