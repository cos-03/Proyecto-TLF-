import unittest

from agroscript.web import analyze_source


class WebAnalysisTests(unittest.TestCase):
    def test_returns_tokens_with_afd_paths_and_the_actual_derivation_tree(self):
        result = analyze_source("programa demo { mostrar(27); }")

        self.assertTrue(result["valid"])
        self.assertEqual(result["tokens"][0]["kind"], "PROGRAMA")
        self.assertEqual(result["tokens"][0]["states"][0], "q0")
        self.assertTrue(all(state == "q1" for state in result["tokens"][0]["states"][1:]))
        self.assertIn("<programa>", result["treeText"])
        self.assertIn("27", result["treeText"])
        self.assertEqual(result["tree"]["label"], "<programa>")

    def test_returns_lexical_and_syntax_errors_from_the_python_analyzers(self):
        result = analyze_source("programa demo { mostrar(1) @ }")

        self.assertFalse(result["valid"])
        self.assertEqual(len(result["lexicalErrors"]), 1)
        self.assertGreaterEqual(len(result["syntaxErrors"]), 1)


if __name__ == "__main__":
    unittest.main()
