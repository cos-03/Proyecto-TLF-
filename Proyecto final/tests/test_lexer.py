import unittest

from agroscript.lexer import Lexer, TABLA
from agroscript.model import TokenKind


class LexerTests(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()

    def test_reserved_words_and_longest_relational_operator(self):
        result = self.lexer.analyze("sino <= 60.5")
        self.assertEqual(
            [token.kind for token in result.tokens[:-1]],
            [TokenKind.ELSE, TokenKind.LESS_EQUAL, TokenKind.NUMBER],
        )
        self.assertEqual(result.tokens[1].states, ("q0", "q15", "q16"))
        self.assertEqual(result.errors, [])

    def test_comment_and_whitespace_are_discarded(self):
        result = self.lexer.analyze('var cafe = "riego óptimo"; # comentario\n')
        self.assertEqual(
            [token.kind for token in result.tokens[:-1]],
            [TokenKind.VAR, TokenKind.ID, TokenKind.ASSIGN,
             TokenKind.STRING, TokenKind.SEMICOLON],
        )
        self.assertEqual(result.tokens[3].value, "riego óptimo")
        self.assertEqual(result.errors, [])

    def test_reports_incomplete_number_operator_string_and_unknown_symbol(self):
        result = self.lexer.analyze('12. ! "sin cerrar\n@')
        self.assertEqual(
            [error.state for error in result.errors],
            ["q0", "q13", "q5", "q0"],
        )

    def test_table_has_27_states_and_absorbing_sink(self):
        self.assertEqual(len(TABLA), 27)
        self.assertTrue(all(destination == "qE" for destination in TABLA["qE"].values()))


if __name__ == "__main__":
    unittest.main()
