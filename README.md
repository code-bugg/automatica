# Laboratory Work №3 — Lexer & Scanner

**Course:** Formal Languages & Finite Automata  
**Author:** *Lungu Ilie*  
**Group:** *FAF-241*  
**Date:** March 2026

---

## Table of Contents

1. [Theory](#theory)
2. [Objectives](#objectives)
3. [Language Choice](#language-choice)
4. [Token Types](#token-types)
5. [Project Structure](#project-structure)
6. [Implementation](#implementation)
   - [Token Representation](#token-representation)
   - [Lexer State and Cursor](#lexer-state-and-cursor)
   - [Whitespace and Comments](#whitespace-and-comments)
   - [Float vs Integer Disambiguation](#float-vs-integer-disambiguation)
   - [Keyword Disambiguation](#keyword-disambiguation)
   - [Error Handling](#error-handling)
   - [Public Entry Point](#public-entry-point)
7. [Results](#results)
8. [Tests](#tests)
9. [Conclusions](#conclusions)
10. [References](#references)

---

## Theory

Lexical analysis is the **first stage** of a compiler or interpreter pipeline. Its responsibility is to read a raw stream of characters and group them into *tokens* — the smallest meaningful units recognised by the language. The component that performs this task is called a **lexer**, **scanner**, or **tokenizer**.

Two related but distinct concepts appear in this domain:

| Term | Definition |
|------|------------|
| **Lexeme** | The raw character sequence extracted from the source (e.g. `3.14`, `sin`, `(`) |
| **Token** | A categorised, typed unit pairing a *type* with the lexeme (e.g. `FLOAT "3.14"`) |

The lexer does not validate grammar. Whether `(sin)` is a meaningful expression is the concern of the *parser* that follows. The lexer only asks: what kind of unit is this?

A hand-written lexer is equivalent to a **deterministic finite automaton (DFA)**. It maintains a position cursor in the source string, transitions on each character according to the current state, and emits a token upon reaching an accepting state. Because every valid token type can be described by a regular expression, the set of all token types forms a **regular language** — precisely the class of languages recognised by DFAs.

The **maximal-munch** (or *longest-match*) rule governs which token to emit when multiple patterns could match at the current position: always consume the longest valid token. For example, `>=` must not be read as `>` followed by `=`; it must be the single two-character token `>=`.

---

## Objectives

1. Understand what lexical analysis is.
2. Get familiar with the inner workings of a lexer / scanner / tokenizer.
3. Implement a sample lexer and demonstrate how it works.

---

## Language Choice

Rather than implementing a plain arithmetic calculator, this work targets a **Lisp-flavored S-expression math language**. Every expression is a fully-parenthesized prefix form:

```
(operator arg1 arg2 ...)
```

This choice is more interesting than a basic calculator for several reasons:

- The grammar is minimal in structure (only parentheses and spaces separate tokens) yet rich in token *categories* (keywords, identifiers, two numeric types, named constants, binding forms).
- It separates the lexer's job from the parser's job very cleanly: the lexer only categorises; the nested structure is entirely a parser concern.
- Variable binding via `define` and `let` means the token set requires identifier recognition and keyword classification — not just number parsing.

**Example programs:**

```lisp
; Euler identity — cos(π) + 1 = 0
(+ (cos pi) 1)

; Pythagorean hypotenuse using let binding
(let ((x 3) (y 4))
  (^ (+ (* x x) (* y y)) 0.5))

; Named constant and trig function
(sin (* pi 0.5))

; Variable definition with scientific notation float
(define earth_radius 6.371e3)

; Circumference using a previously defined variable
(* 2 pi earth_radius)
```

---

## Token Types

The lexer recognises **18 distinct token types**, grouped by category:

| Category | Token types | Examples |
|----------|------------|---------|
| Delimiters | `LPAREN`, `RPAREN` | `(`, `)` |
| Arithmetic operators | `PLUS`, `MINUS`, `STAR`, `SLASH`, `CARET` | `+`, `-`, `*`, `/`, `^` |
| Integer literals | `INTEGER` | `42`, `0`, `100` |
| Float literals | `FLOAT` | `3.14`, `.5`, `1.5e2`, `2E-3` |
| Trig functions | `SIN`, `COS`, `TAN` | `sin`, `cos`, `tan` |
| Named constants | `PI`, `E_CONST` | `pi`, `e` |
| Binding keywords | `DEFINE`, `LET` | `define`, `let` |
| General identifier | `IDENT` | `radius`, `x`, `my_var` |
| Sentinel | `EOF` | *(end of input)* |

---

## Project Structure

```
lexer/
├── lexer.py    # TokenType enum, Token dataclass, _Lexer class, tokenize() entry point
├── demo.py     # 10 runnable examples covering all token categories and the error case
├── tests.py    # 28 unit tests across 8 test classes
└── REPORT.md   # This document
```

The public interface consists of three names:

```python
from lexer import tokenize, Token, LexError
```

`tokenize(source: str) -> list[Token]` is the only function consumers need.

---

## Implementation

### Token Representation

Each token is an immutable `dataclass` carrying three fields:

```python
class TokenType(Enum):
    LPAREN = auto()
    RPAREN = auto()
    INTEGER = auto()
    FLOAT   = auto()
    PLUS    = auto()
    MINUS   = auto()
    STAR    = auto()
    SLASH   = auto()
    CARET   = auto()
    SIN     = auto()
    COS     = auto()
    TAN     = auto()
    PI      = auto()
    E_CONST = auto()
    DEFINE  = auto()
    LET     = auto()
    IDENT   = auto()
    EOF     = auto()

@dataclass
class Token:
    type:  TokenType
    value: str       # raw lexeme text
    line:  int       # 1-based line number
    col:   int       # 1-based column number
```

The `line` and `col` fields are not strictly required by this lab, but they are essential in any real compiler for producing useful error messages, and they make the output much easier to read.

---

### Lexer State and Cursor

The `_Lexer` class holds all mutable state for a single tokenization run. Three cursor primitives drive everything:

```python
class _Lexer:
    def __init__(self, source: str) -> None:
        self._src  = source
        self._pos  = 0      # current character index
        self._line = 1      # 1-based line counter
        self._col  = 1      # 1-based column counter

    def peek(self, offset: int = 0) -> str | None:
        """Non-consuming lookahead. Returns None past end-of-source."""
        idx = self._pos + offset
        return self._src[idx] if idx < len(self._src) else None

    def advance(self) -> str:
        """Consume the current character, updating line/col tracking."""
        ch = self._src[self._pos]
        self._pos += 1
        if ch == "\n":
            self._line += 1
            self._col   = 1
        else:
            self._col  += 1
        return ch

    def at_end(self) -> bool:
        return self._pos >= len(self._src)
```

The main loop calls `_next_token()` until `EOF`:

```python
def tokenize(self) -> list[Token]:
    tokens = []
    while True:
        tok = self._next_token()
        tokens.append(tok)
        if tok.type is TokenType.EOF:
            break
    return tokens
```

---

### Whitespace and Comments

Before every token attempt the lexer silently skips spaces, tabs, newlines, and `;`-prefixed line comments. PolarPandas uses `#`; the S-expression language uses `;` — the convention of the Lisp family.

```python
def _skip_whitespace_and_comments(self):
    while self._pos < len(self._src):
        ch = self.peek()
        if ch in (" ", "\t", "\r", "\n"):
            self.advance()
        elif ch == ";":                     # ; comment to end of line
            while self.peek() not in (None, "\n"):
                self.advance()
        else:
            break
```

This ensures that comments are completely transparent to all downstream stages.

---

### Float vs Integer Disambiguation

The dispatcher attempts to match a **float** before an **integer** at every digit position. This is critical: without this ordering, `3.14` would be consumed as the integer `3` followed by an unrecognised `.14`.

Three float forms are recognised via a single compiled regex:

```python
_FLOAT_RE = re.compile(
    r"\d+\.\d*(?:[eE][+-]?\d+)?"   # 3.14  3.  3.14e2
    r"|\.\d+(?:[eE][+-]?\d+)?"     # .5    .5e-3
    r"|\d+[eE][+-]?\d+"            # 1e3   2E-4
)
_INT_RE = re.compile(r"\d+")
```

Dispatch:

```python
# In _next_token():
float_text = self._match_re(_FLOAT_RE)
if float_text is not None:
    return Token(TokenType.FLOAT, float_text, line, col)

int_text = self._match_re(_INT_RE)
if int_text is not None:
    return Token(TokenType.INTEGER, int_text, line, col)
```

The helper `_match_re` attempts to match the pattern at the current position and, if successful, advances the cursor by the length of the match before returning the text:

```python
def _match_re(self, pattern: re.Pattern) -> str | None:
    m = pattern.match(self._src, self._pos)
    if m:
        text = m.group()
        for _ in text:
            self.advance()
        return text
    return None
```

---

### Keyword Disambiguation

Identifiers and keywords share the same character class: `[A-Za-z_][A-Za-z0-9_]*`. The lexer first consumes the **entire word** greedily, then looks it up in the keyword table:

```python
KEYWORDS: dict[str, TokenType] = {
    "sin": TokenType.SIN,   "cos": TokenType.COS,   "tan": TokenType.TAN,
    "pi":  TokenType.PI,    "e":   TokenType.E_CONST,
    "define": TokenType.DEFINE,  "let": TokenType.LET,
}

ident_text = self._match_re(_IDENT_RE)   # greedy: [A-Za-z_][A-Za-z0-9_]*
if ident_text is not None:
    ttype = KEYWORDS.get(ident_text, TokenType.IDENT)
    return Token(ttype, ident_text, line, col)
```

This is the correct application of the maximal-munch rule to identifiers: the word `sinusoidal` is consumed in one step as an `IDENT`, not split into `SIN` + `usoidal`. A character-by-character keyword check would fail this case.

---

### Error Handling

When no pattern matches the current character a `LexError` is raised with both the offending character and its position:

```python
class LexError(Exception):
    def __init__(self, message: str, line: int, col: int):
        super().__init__(f"{message} (line {line}, col {col})")
        self.line = line
        self.col  = col
```

The dispatcher always falls through to this after all valid patterns have been tried:

```python
# Unreachable via valid input — but always present as a safety net
raise LexError(f"Unexpected character {ch!r}", line, col)
```

---

### Public Entry Point

The module exposes a single stateless function. A new `_Lexer` instance is created for every call, so `tokenize()` is safe to call concurrently and has no global side effects:

```python
def tokenize(source: str) -> list[Token]:
    """
    Lex an S-expression math source string into an ordered list of tokens.
    The final token is always Token(EOF, "", ...).
    Raises LexError on any unrecognised character.
    """
    return _Lexer(source).tokenize()
```

---

## Results

Below are the outputs produced by running `demo.py`.

#### Basic arithmetic

```
Input: (+ 1 2)
```
```
Token(LPAREN   '('   ln=1, col=1)
Token(PLUS     '+'   ln=1, col=2)
Token(INTEGER  '1'   ln=1, col=4)
Token(INTEGER  '2'   ln=1, col=6)
Token(RPAREN   ')'   ln=1, col=7)
Token(EOF      ''    ln=1, col=8)
```

#### Trig + named constant

```
Input: (sin (* pi 0.5))
```
```
Token(LPAREN   '('    ln=1, col=1)
Token(SIN      'sin'  ln=1, col=2)
Token(LPAREN   '('    ln=1, col=6)
Token(STAR     '*'    ln=1, col=7)
Token(PI       'pi'   ln=1, col=9)
Token(FLOAT    '0.5'  ln=1, col=12)
Token(RPAREN   ')'    ln=1, col=15)
Token(RPAREN   ')'    ln=1, col=16)
Token(EOF      ''     ln=1, col=17)
```

#### Float literals (scientific and leading-dot)

```
Input: (* 1.5e2 .75)
```
```
Token(LPAREN   '('      ln=1, col=1)
Token(STAR     '*'      ln=1, col=2)
Token(FLOAT    '1.5e2'  ln=1, col=4)
Token(FLOAT    '.75'    ln=1, col=10)
Token(RPAREN   ')'      ln=1, col=13)
Token(EOF      ''       ln=1, col=14)
```

#### Variable definition

```
Input: (define radius 6.371e3)
```
```
Token(LPAREN   '('        ln=1, col=1)
Token(DEFINE   'define'   ln=1, col=2)
Token(IDENT    'radius'   ln=1, col=9)
Token(FLOAT    '6.371e3'  ln=1, col=16)
Token(RPAREN   ')'        ln=1, col=23)
Token(EOF      ''         ln=1, col=24)
```

#### Pythagorean — let binding

```
Input: (let ((x 3) (y 4)) (^ (+ (* x x) (* y y)) 0.5))
```
```
Token(LPAREN   '('    ln=1, col=1)
Token(LET      'let'  ln=1, col=2)
Token(LPAREN   '('    ln=1, col=6)
Token(LPAREN   '('    ln=1, col=7)
Token(IDENT    'x'    ln=1, col=8)
Token(INTEGER  '3'    ln=1, col=10)
Token(RPAREN   ')'    ln=1, col=11)
Token(LPAREN   '('    ln=1, col=13)
Token(IDENT    'y'    ln=1, col=14)
Token(INTEGER  '4'    ln=1, col=16)
Token(RPAREN   ')'    ln=1, col=17)
Token(RPAREN   ')'    ln=1, col=18)
Token(LPAREN   '('    ln=1, col=20)
Token(CARET    '^'    ln=1, col=21)
... (remaining tokens omitted for brevity)
Token(EOF      ''     ln=1, col=48)
```

#### Comment skipping

```
Input: "; circumference\n(* 2 pi radius)"
```
```
Token(LPAREN   '('       ln=2, col=1)
Token(STAR     '*'       ln=2, col=2)
Token(INTEGER  '2'       ln=2, col=4)
Token(PI       'pi'      ln=2, col=6)
Token(IDENT    'radius'  ln=2, col=9)
Token(RPAREN   ')'       ln=2, col=15)
Token(EOF      ''        ln=2, col=16)
```

Note that the `; circumference` comment on line 1 produces no tokens at all, and the subsequent tokens correctly report line 2.

#### Error case

```
Input: (+ 1 @2)
```
```
LexError: Unexpected character '@' (line 1, col 6)
```

---

## Tests

`tests.py` contains **28 unit tests** across 8 test classes, runnable with `python tests.py` (no dependencies beyond the standard library):

| Class | Tests | What is covered |
|-------|-------|----------------|
| `TestDelimiters` | 2 | `(` `)` emission |
| `TestNumbers` | 5 | Integers, standard floats, scientific notation, leading-dot floats, no float/int confusion |
| `TestOperators` | 1 | All five arithmetic operators |
| `TestKeywords` | 4 | `sin`/`cos`/`tan`, `pi`/`e`, `define`/`let`, keyword-prefix safety (`sink` ≠ `SIN` + `k`) |
| `TestIdentifiers` | 3 | Simple, underscore-prefixed, mixed-case identifiers |
| `TestWhitespaceAndComments` | 4 | Spaces, newlines, `;` comments, comment does not consume next line |
| `TestLineAndCol` | 2 | Column tracking on a single line; line tracking across newlines |
| `TestComplexExpressions` | 4 | `(sin (* pi 0.5))`, `(define r …)`, `(let …)`, `(^ …)` |
| `TestErrors` | 3 | `LexError` raised on `@`, error reports correct line and column, `#` is invalid |

All 28 tests pass.

```
----------------------------------------------------------------------
Ran 28 tests in 0.002s

OK
```

A selected test illustrating the keyword-prefix safety check — the most commonly missed edge case in student lexer implementations:

```python
def test_keyword_not_prefix_matched(self):
    # "sink" starts with "sin" but must be classified as IDENT, not SIN
    self.assertEqual(types("sink"), [TokenType.IDENT])
    self.assertEqual(values("sink"), ["sink"])
```

This passes because the lexer always consumes the full identifier greedily before doing the keyword lookup, rather than checking keywords character-by-character.

---

## Conclusions

This laboratory work provided hands-on experience with the first stage of language processing. The key takeaways are:

1. **Categorisation only.** The lexer's job is purely to assign token types to character sequences. It makes no structural judgments — whether a sequence of tokens forms a valid expression is the parser's responsibility.

2. **Priority ordering is load-bearing.** The dispatch order in `_next_token` is not arbitrary. Float must be attempted before integer (so `3.14` is not split as `3` + `.14`), and the full identifier must be consumed before keyword lookup (so `sinusoidal` is not split as `SIN` + `usoidal`). Getting this order wrong produces subtle bugs that are hard to find without a thorough test suite.

3. **Position tracking is worth the effort.** Carrying `line` and `col` on every token adds very little complexity but makes error messages immediately useful. Without it, debugging a LexError is significantly harder.

4. **S-expressions were a good choice.** The minimal syntax kept the lexer implementation clean while the variety of token categories (trig keywords, named constants, two numeric types, binding forms) made the exercise non-trivial and more interesting than a basic calculator.

A natural extension would be to build a recursive-descent parser on top of this lexer to evaluate expressions, followed by an interpreter that resolves `define` bindings and evaluates `let` scopes.

---

## References

[1] [LLVM Tutorial — My First Language Frontend](https://llvm.org/docs/tutorial/MyFirstLanguageFrontend/LangImpl01.html)  
[2] [Lexical Analysis — Wikipedia](https://en.wikipedia.org/wiki/Lexical_analysis)
