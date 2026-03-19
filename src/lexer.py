"""
Lexer for a Lisp-flavored S-expression math language.

Supports:
  - S-expression syntax: (op arg1 arg2 ...)
  - Arithmetic operators: +  -  *  /  ^
  - Trig functions: sin  cos  tan
  - Named constants: pi  e
  - Variable binding: define  let
  - Integers and floats (including negative via unary -)
  - Identifiers (variable names)
  - Single-line comments  ; like this
"""

from __future__ import annotations
import re
from dataclasses import dataclass
from enum import Enum, auto
from typing import List


# ── Token types ────────────────────────────────────────────────────────────────

class TokenType(Enum):
    # Delimiters
    LPAREN    = auto()   # (
    RPAREN    = auto()   # )

    # Literals
    INTEGER   = auto()   # 42
    FLOAT     = auto()   # 3.14  |  .5  |  1e-3

    # Operators
    PLUS      = auto()   # +
    MINUS     = auto()   # -
    STAR      = auto()   # *
    SLASH     = auto()   # /
    CARET     = auto()   # ^

    # Trig functions
    SIN       = auto()
    COS       = auto()
    TAN       = auto()

    # Named constants
    PI        = auto()
    E_CONST   = auto()   # e  (Euler's number)

    # Variable binding keywords
    DEFINE    = auto()   # (define name expr)
    LET       = auto()   # (let ((name expr) ...) body)

    # General identifier  (variable name not matching a keyword)
    IDENT     = auto()

    # End of input
    EOF       = auto()


# ── Token dataclass ─────────────────────────────────────────────────────────────

@dataclass
class Token:
    type:   TokenType
    value:  str
    line:   int
    col:    int

    def __repr__(self) -> str:
        return f"Token({self.type.name}, {self.value!r}, ln={self.line}, col={self.col})"


# ── Keyword / symbol tables ─────────────────────────────────────────────────────

KEYWORDS: dict[str, TokenType] = {
    "sin":    TokenType.SIN,
    "cos":    TokenType.COS,
    "tan":    TokenType.TAN,
    "pi":     TokenType.PI,
    "e":      TokenType.E_CONST,
    "define": TokenType.DEFINE,
    "let":    TokenType.LET,
}

SINGLE_CHAR: dict[str, TokenType] = {
    "(": TokenType.LPAREN,
    ")": TokenType.RPAREN,
    "+": TokenType.PLUS,
    "-": TokenType.MINUS,
    "*": TokenType.STAR,
    "/": TokenType.SLASH,
    "^": TokenType.CARET,
}

# Regex patterns (applied in order — first match wins)
_FLOAT_RE   = re.compile(r"\d+\.\d*(?:[eE][+-]?\d+)?|\.\d+(?:[eE][+-]?\d+)?|\d+[eE][+-]?\d+")
_INT_RE     = re.compile(r"\d+")
_IDENT_RE   = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


# ── LexError ───────────────────────────────────────────────────────────────────

class LexError(Exception):
    def __init__(self, message: str, line: int, col: int):
        super().__init__(f"{message} (line {line}, col {col})")
        self.line = line
        self.col  = col


# ── Lexer ──────────────────────────────────────────────────────────────────────

class Lexer:
    """
    Hand-written single-pass lexer.

    Usage
    -----
        lexer  = Lexer("(define x (cos (* pi 2)))")
        tokens = lexer.tokenize()
    """

    def __init__(self, source: str):
        self._src  = source
        self._pos  = 0          # current character index
        self._line = 1
        self._col  = 1

    # ── public API ─────────────────────────────────────────────────────────────

    def tokenize(self) -> List[Token]:
        tokens: List[Token] = []
        while True:
            tok = self._next_token()
            tokens.append(tok)
            if tok.type is TokenType.EOF:
                break
        return tokens

    # ── internal helpers ───────────────────────────────────────────────────────

    def _peek(self, offset: int = 0) -> str | None:
        idx = self._pos + offset
        return self._src[idx] if idx < len(self._src) else None

    def _advance(self) -> str:
        ch = self._src[self._pos]
        self._pos += 1
        if ch == "\n":
            self._line += 1
            self._col   = 1
        else:
            self._col  += 1
        return ch

    def _skip_whitespace_and_comments(self):
        while self._pos < len(self._src):
            ch = self._peek()
            if ch in (" ", "\t", "\r", "\n"):
                self._advance()
            elif ch == ";":                     # line comment
                while self._peek() not in (None, "\n"):
                    self._advance()
            else:
                break

    def _match_re(self, pattern: re.Pattern) -> str | None:
        m = pattern.match(self._src, self._pos)
        if m:
            text = m.group()
            for _ in text:
                self._advance()
            return text
        return None

    # ── token dispatch ─────────────────────────────────────────────────────────

    def _next_token(self) -> Token:
        self._skip_whitespace_and_comments()

        line, col = self._line, self._col

        if self._pos >= len(self._src):
            return Token(TokenType.EOF, "", line, col)

        ch = self._peek()

        # Single-character tokens
        if ch in SINGLE_CHAR:
            self._advance()
            return Token(SINGLE_CHAR[ch], ch, line, col)

        # Numbers: try float first (more specific), then int
        float_text = self._match_re(_FLOAT_RE)
        if float_text is not None:
            return Token(TokenType.FLOAT, float_text, line, col)

        int_text = self._match_re(_INT_RE)
        if int_text is not None:
            return Token(TokenType.INTEGER, int_text, line, col)

        # Identifiers and keywords
        ident_text = self._match_re(_IDENT_RE)
        if ident_text is not None:
            ttype = KEYWORDS.get(ident_text, TokenType.IDENT)
            return Token(ttype, ident_text, line, col)

        # Unknown character
        raise LexError(f"Unexpected character {ch!r}", line, col)