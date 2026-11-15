import unittest
from unittest.mock import patch

from agroscript.cli import main
from agroscript.lexer import analyze
from agroscript.parser import parse
from agroscript.tree import render_tree


class ParserTests(unittest.TestCase):
    def test_parses_full_domain_example_and_builds_derivation_tree(self):
        with open("ejemplos/riego_valido.agro", encoding="utf-8") as file:
            result = analyze(file.read())
        tree, errors = parse(result.tokens)
        self.assertEqual(result.errors, [])
        self.assertEqual(errors, [])
        self.assertIsNotNone(tree)
        rendered = render_tree(tree)
        self.assertIn("<condicional>", rendered)
        self.assertIn("<ciclo>", rendered)
        self.assertIn("<sino_opt>", rendered)
        self.assertIn("ε", rendered)

    def test_expression_tree_preserves_precedence_structure(self):
        source = "programa demo { mostrar(1 + 2 * 3); }"
        tree, errors = parse(analyze(source).tokens)
        self.assertEqual(errors, [])
        rendered = render_tree(tree)
        self.assertLess(rendered.index("MAS"), rendered.index("POR"))

    def test_empty_program_block_is_valid(self):
        tree, errors = parse(analyze("programa demo {}").tokens)
        self.assertIsNotNone(tree)
        self.assertEqual(errors, [])

    def test_rejects_missing_program_delimiters(self):
        tree, errors = parse(analyze("programa demo { mostrar(1);").tokens)
        self.assertIsNone(tree)
        self.assertEqual(len(errors), 1)

    @patch("agroscript.cli.webbrowser.open", return_value=True)
    def test_opens_html_when_no_source_is_given(self, mock_open):
        result = main([])
        self.assertEqual(result, 0)
        mock_open.assert_called_once()
        self.assertIn("index.html", mock_open.call_args[0][0])


if __name__ == "__main__":
    unittest.main()
