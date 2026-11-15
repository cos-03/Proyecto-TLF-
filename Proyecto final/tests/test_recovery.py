import unittest

from agroscript.lexer import analyze
from agroscript.parser import parse


class RecoveryTests(unittest.TestCase):
    def test_reports_multiple_errors_and_continues_at_next_statement(self):
        source = """programa demo {
            var x = 1
            var y = (2 + ;
            mostrar(x);
        }"""
        result = analyze(source)
        tree, errors = parse(result.tokens)
        self.assertEqual(result.errors, [])
        self.assertGreaterEqual(len(errors), 2)
        self.assertIsNotNone(tree)
        self.assertTrue(all(error.line >= 2 for error in errors))

    def test_lexical_and_syntax_errors_can_be_reported_together(self):
        source = "programa demo { var x = 1 @ 2; mostrar(x); }"
        result = analyze(source)
        _, errors = parse(result.tokens)
        self.assertEqual(len(result.errors), 1)
        self.assertGreaterEqual(len(errors), 1)


if __name__ == "__main__":
    unittest.main()
