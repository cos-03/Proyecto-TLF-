"""Renderizado textual del árbol de derivación."""

from __future__ import annotations

from .model import ParseNode


def render_tree(root: ParseNode) -> str:
    lines = [root.label]

    def visit(node: ParseNode, prefix: str) -> None:
        for index, child in enumerate(node.children):
            last = index == len(node.children) - 1
            lines.append(prefix + ("└── " if last else "├── ") + child.label)
            visit(child, prefix + ("    " if last else "│   "))

    visit(root, "")
    return "\n".join(lines)
