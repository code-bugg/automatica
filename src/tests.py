"""
tests.py — unit tests for the S-expression math lexer.
Run with:  python -m pytest tests.py -v
       or  python tests.py
"""

import unittest
from lexer import Lexer, LexError, TokenType


def types(source: str):
    """Return just the TokenType list (excluding EOF) for a source string."""
    return [t.type for t in Lexer(source).tokenize() if t.type is not TokenType.EOF]


def values(source: str):
    """Return just the lexeme value list (excluding EOF)."""
    return [t.value for t in Lexer(source).tokenize() if t.type is not TokenType.EOF]


class TestDelimiters(unittest.TestCase):
    def test_empty_parens(self):
        self.assertEqual(types("()"), [TokenType.LPAREN, TokenType.RPAREN])

    def test_nested_parens(self):
        self.assertEqual(
            types("(())"),
            [TokenType.LPAREN, TokenType.LPAREN, TokenType.RPAREN, TokenType.RPAREN],
        )


class TestNumbers(unittest.TestCase):
    def test_integer(self):
        self.assertEqual(types("42"), [TokenType.INTEGER])
        self.assertEqual(values("42"), ["42"])

    def test_float_standard(self):
        self.assertEqual(types("3.14"), [TokenType.FLOAT])

    def test_float_leading_dot(self):
        self.assertEqual(types(".5"), [TokenType.FLOAT])
        self.assertEqual(values(".5"), [".5"])

    def test_float_scientific(self):
        self.assertEqual(types("1.5e2"), [TokenType.FLOAT])
        self.assertEqual(types("2E-3"), [TokenType.FLOAT])

    def test_integer_not_swallowed_as_float(self):
        self.assertEqual(types("7"), [TokenType.INTEGER])


class TestOperators(unittest.TestCase):
    def test_all_operators(self):
        self.assertEqual(
            types("+ - * / ^"),
            [TokenType.PLUS, TokenType.MINUS, TokenType.STAR, TokenType.SLASH, TokenType.CARET],
        )


class TestKeywords(unittest.TestCase):
    def test_trig(self):
        self.assertEqual(types("sin"), [TokenType.SIN])
        self.assertEqual(types("cos"), [TokenType.COS])
        self.assertEqual(types("tan"), [TokenType.TAN])

    def test_constants(self):
        self.assertEqual(types("pi"), [TokenType.PI])
        self.assertEqual(types("e"),  [TokenType.E_CONST])

    def test_binding_keywords(self):
        self.assertEqual(types("define"), [TokenType.DEFINE])
        self.assertEqual(types("let"),    [TokenType.LET])

    def test_keyword_not_prefix_matched(self):
        # "sink" starts with "sin" but is an identifier, not SIN
        self.assertEqual(types("sink"), [TokenType.IDENT])
        self.assertEqual(values("sink"), ["sink"])


class TestIdentifiers(unittest.TestCase):
    def test_simple_ident(self):
        self.assertEqual(types("radius"), [TokenType.IDENT])

    def test_underscore_ident(self):
        self.assertEqual(types("_x1"), [TokenType.IDENT])

    def test_mixed_case(self):
        self.assertEqual(types("MyVar"), [TokenType.IDENT])


class TestWhitespaceAndComments(unittest.TestCase):
    def test_whitespace_ignored(self):
        self.assertEqual(types("  (  +  1  2  )  "),
                         [TokenType.LPAREN, TokenType.PLUS, TokenType.INTEGER,
                          TokenType.INTEGER, TokenType.RPAREN])

    def test_newline_ignored(self):
        self.assertEqual(types("1\n2"), [TokenType.INTEGER, TokenType.INTEGER])

    def test_comment_ignored(self):
        self.assertEqual(types("; this is a comment\n1"), [TokenType.INTEGER])

    def test_comment_does_not_consume_next_line(self):
        result = types("; comment\n(+ 1 2)")
        self.assertIn(TokenType.PLUS, result)


class TestLineAndCol(unittest.TestCase):
    def test_single_line_col(self):
        tokens = {t.type: t for t in Lexer("(+ 1)").tokenize()}
        self.assertEqual(tokens[TokenType.LPAREN].col, 1)
        self.assertEqual(tokens[TokenType.PLUS].col,   2)
        self.assertEqual(tokens[TokenType.INTEGER].col, 4)

    def test_multiline_tracking(self):
        src = "(+\n  1\n  2)"
        toks = [t for t in Lexer(src).tokenize() if t.type is not TokenType.EOF]
        one = next(t for t in toks if t.value == "1")
        two = next(t for t in toks if t.value == "2")
        self.assertEqual(one.line, 2)
        self.assertEqual(two.line, 3)


class TestComplexExpressions(unittest.TestCase):
    def test_sin_of_pi(self):
        toks = types("(sin (* pi 0.5))")
        self.assertIn(TokenType.SIN, toks)
        self.assertIn(TokenType.PI,  toks)
        self.assertIn(TokenType.FLOAT, toks)

    def test_define(self):
        toks = types("(define r 6.371e3)")
        self.assertEqual(toks[1], TokenType.DEFINE)
        self.assertEqual(toks[2], TokenType.IDENT)
        self.assertEqual(toks[3], TokenType.FLOAT)

    def test_let_binding(self):
        src = "(let ((x 3) (y 4)) (+ x y))"
        toks = types(src)
        self.assertEqual(toks[0], TokenType.LPAREN)
        self.assertEqual(toks[1], TokenType.LET)

    def test_pythagorean(self):
        src = "(^ (+ (* x x) (* y y)) 0.5)"
        toks = types(src)
        self.assertIn(TokenType.CARET, toks)
        self.assertIn(TokenType.STAR,  toks)


class TestErrors(unittest.TestCase):
    def test_unknown_char(self):
        with self.assertRaises(LexError):
            Lexer("(+ 1 @2)").tokenize()

    def test_error_position(self):
        try:
            Lexer("(+ 1 @2)").tokenize()
        except LexError as err:
            self.assertEqual(err.line, 1)
            self.assertEqual(err.col,  6)

    def test_hash_is_invalid(self):
        with self.assertRaises(LexError):
            Lexer("#t").tokenize()


if __name__ == "__main__":
    unittest.main(verbosity=2)