"""Punto de entrada para AgroScript."""

import sys

from agroscript.cli import main


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
