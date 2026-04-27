# Parser & Abstract Syntax Tree

**Course:** Formal Languages & Finite Automata  
**Author:** \<your name\>  
**Group:** FAF-241  

---

## Theory

**Parsing** is the process of analysing a sequence of tokens to determine its grammatical structure according to a formal grammar. The output of a parser is typically a tree that represents how the tokens relate to one another — a **parse tree** if every grammar rule is reflected, or an **Abstract Syntax Tree (AST)** if only the semantically relevant structure is kept.

An **AST** is a hierarchical data structure whose nodes represent constructs of the source language (statements, expressions, literals) and whose edges represent containment or sequencing. Unlike a raw parse tree, an AST omits punctuation tokens (parentheses, commas, pipe operators) that exist only to guide the parser but carry no information once parsing is complete. ASTs are the standard internal representation used by compilers, interpreters, linters, and code-analysis tools for all subsequent processing stages.

A **recursive-descent parser** implements the grammar directly as a set of mutually recursive functions, one per non-terminal. It is a top-down, predictive approach that is easy to write by hand and produces good error messages — ideal for domain-specific languages.

---

## Objectives

1. Consolidate Lab 3 by adding a formal `TokenType` enum backed by regular expressions.
2. Design a complete AST node hierarchy for the PolarPandas DSL.
3. Implement a recursive-descent parser that converts a token stream into an AST.
4. Demonstrate the full pipeline — source text → tokens → AST — on representative input.

---

## Implementation

Everything lives in a single `main.py` file, organised into six layers.

### 1 — TokenType enum

```python
class TokenType(Enum):
    NUMBER, STRING, BOOL, IDENTIFIER, KEYWORD,
    PIPE, ASSIGN, COMMA, COLON,
    LPAREN, RPAREN, LBRACKET, RBRACKET,
    NEWLINE, INDENT, DEDENT, EOF
```

17 token types, unchanged from the Lab 3 specification. Each type is paired with a compiled regex in the `TOKEN_PATTERNS` list, which the lexer tries in order for every character position:

```python
TOKEN_PATTERNS = [
    (TokenType.NUMBER,     re.compile(r'-?\d+(\.\d+)?')),
    (TokenType.STRING,     re.compile(r'"[^"]*"|\'[^\']*\'')),
    (TokenType.BOOL,       re.compile(r'\b(true|false)\b')),
    (TokenType.PIPE,       re.compile(r'->')),
    (TokenType.IDENTIFIER, re.compile(r'(>=|<=|!=|==)')),
    (TokenType.IDENTIFIER, re.compile(r'[><!]')),
    (TokenType.ASSIGN,     re.compile(r'=')),
    ...
]
```

After a raw match, the lexer promotes `IDENTIFIER` tokens whose value is in the `KEYWORDS` set to `TokenType.KEYWORD`, and promotes `true`/`false` to `TokenType.BOOL`. This keeps the pattern list clean while handling keyword disambiguation in one place.

---

### 2 — Lexer

The `Lexer` class processes source text line-by-line and emits a flat list of `Token` objects. Each token carries its type, string value, and source position (line, column) for error reporting. Indentation tracking uses a stack of indent levels to emit synthetic `INDENT` / `DEDENT` tokens, and inline comments (`#`) are stripped before tokenisation.

---

### 3 — AST node hierarchy

All nodes are **frozen dataclasses** that inherit from `ASTNode`. Frozen dataclasses are immutable and hashable, which makes the AST safe to inspect from multiple passes without risk of accidental mutation.

The nodes fall into four groups:

**Literals and atoms**

| Node | Fields |
|---|---|
| `NumberLiteral` | `value: float` |
| `StringLiteral` | `value: str` |
| `BoolLiteral` | `value: bool` |
| `Identifier` | `name: str` |

**Expressions**

| Node | Purpose |
|---|---|
| `ColumnList` | Ordered tuple of column name strings |
| `BinaryOp` | `left op right` comparison (e.g. `age > 30`) |
| `LogicalOp` | `and` / `or` of two sub-conditions |
| `NotOp` | Logical negation |
| `AggCall` | Aggregation call such as `sum(revenue)` |
| `KwArg` | Keyword argument `key=value` in steps like `plot` |

**Pipeline steps** (one node per DSL keyword)

`LoadStep`, `SaveStep`, `FilterStep`, `SelectStep`, `GroupByStep`, `AggStep`, `SortStep`, `PlotStep`, `ShowStep`, `DescribeStep`, `LimitStep`

**Top-level structure**

| Node | Fields |
|---|---|
| `Pipeline` | `name: str \| None`, `steps: tuple[ASTNode, ...]` |
| `Program` | `pipelines: tuple[Pipeline, ...]` — the root node |

---

### 4 — Parser

`Parser` is a recursive-descent parser that consumes the flat token list produced by the lexer. `INDENT` and `DEDENT` tokens are stripped before parsing begins because pipeline syntax is expressed on single logical lines connected by `->` operators.

The grammar implemented (informal notation):

```
program   = pipeline* EOF
pipeline  = [IDENTIFIER '='] step ('->' step)* NEWLINE
step      = load | save | filter | select | groupby
          | agg | sort | plot | show | describe | limit

condition = or_expr
or_expr   = and_expr ('or' and_expr)*
and_expr  = not_expr ('and' not_expr)*
not_expr  = 'not' not_expr | compare
compare   = atom (OP atom)?
atom      = NUMBER | STRING | BOOL | IDENTIFIER | '(' condition ')'
```

Three helper methods underpin all rules:

```python
_check(type, value)  →  bool      # peek without consuming
_match(type, value)  →  bool      # consume if match
_expect(type, value) →  Token     # consume or raise ParseError
```

Operator precedence for conditions is handled by the call stack: `_parse_or` calls `_parse_and`, which calls `_parse_not`, which calls `_parse_compare`. Each level only handles its own operator, so precedence is implicit and correct.

---

### 5 — AST pretty-printer

`print_ast(node, indent)` uses Python's structural `match` statement to dispatch on node type and prints a human-readable tree. No node is handled by a generic fallback — each case is explicit, which means a missing case raises a `MatchError` immediately rather than silently printing nothing.

---

## Example

**Input:**

```
result = load("data/sales.csv") -> filter(region == "EU") -> select[region, revenue, units] -> sort[revenue] descending -> limit(10) -> show

summary = load("data/sales.csv", engine=polars) -> filter(revenue > 1000 and not region == "US") -> groupby[region] -> agg(sum(revenue), mean(units)) -> sort[revenue] descending -> plot(bar, title="Revenue by Region", xlabel="Region", ylabel="Revenue") -> save("output/summary.csv")
```

**Token stream (excerpt):**

```
Token(IDENTIFIER, 'result',  2:1)
Token(ASSIGN,     '=',       2:8)
Token(KEYWORD,    'load',    2:10)
Token(LPAREN,     '(',       2:14)
Token(STRING,     '"data/sales.csv"', 2:15)
Token(RPAREN,     ')',       2:31)
Token(PIPE,       '->',      2:33)
Token(KEYWORD,    'filter',  2:36)
Token(IDENTIFIER, '==',      2:50)
...
```

**AST output:**

```
Program
  Pipeline [result]
    LoadStep  engine=default
      String('data/sales.csv')
    FilterStep
      BinaryOp  op='=='
        Identifier('region')
        String('EU')
    SelectStep  cols=['region', 'revenue', 'units']
    SortStep  descending  cols=['revenue']
    LimitStep  n=10
    ShowStep
  Pipeline [summary]
    LoadStep  engine=polars
      String('data/sales.csv')
    FilterStep
      LogicalOp  op='and'
        BinaryOp  op='>'
          Identifier('revenue')
          Number(1000.0)
        NotOp
          BinaryOp  op='=='
            Identifier('region')
            String('US')
    GroupByStep  cols=['region']
    AggStep
      AggCall  sum(revenue)
      AggCall  mean(units)
    SortStep  descending  cols=['revenue']
    PlotStep  kind=bar
      KwArg  key='title'
        String('Revenue by Region')
      KwArg  key='xlabel'
        String('Region')
      KwArg  key='ylabel'
        String('Revenue')
    SaveStep
      String('output/summary.csv')
```

---

## Conclusions

- **Frozen dataclasses** are the right tool for AST nodes: they are concise to define, structurally equal by value (useful in tests), and immutable by construction. Python's `match` statement can destructure them cleanly without any extra boilerplate.
- **Operator precedence** falls out naturally from the recursive-descent call chain. Adding a new precedence level (e.g. bitwise operators) requires inserting exactly one new function between two existing ones — no tables, no refactoring.
- **Token enrichment at lex time** (promoting identifiers to keywords) keeps the grammar rules free of keyword-specific checks and simplifies the `_parse_step` dispatch table significantly.
- **Stripping INDENT/DEDENT before parsing** is valid for PolarPandas because the DSL is single-line by design: every pipeline is one logical line connected by `->`. If block-structured constructs are added in a future version, indentation handling would need to move into the parser.
- The AST is a complete, structured representation of the source. Every node contains all information needed for downstream passes — a code generator targeting pandas/polars or a semantic validator can walk the tree without ever touching the original source text again.