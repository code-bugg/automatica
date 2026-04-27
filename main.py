"""
Lab 6 — Parser & Abstract Syntax Tree
PolarPandas DSL  |  FAF-241

Builds on the Lab 3 lexer.  Adds:
  - TokenType enum  (with regex patterns)
  - 20 frozen AST dataclasses
  - Recursive-descent parser  →  Program AST
  - Pretty-printer for the AST
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any


# ═══════════════════════════════════════════════════════════════════════════════
#  1.  TOKEN TYPES  (enum + regex patterns)
# ═══════════════════════════════════════════════════════════════════════════════

class TokenType(Enum):
    # literals
    NUMBER     = auto()
    STRING     = auto()
    BOOL       = auto()
    # names
    IDENTIFIER = auto()
    KEYWORD    = auto()
    # operators / punctuation
    PIPE       = auto()   # ->
    ASSIGN     = auto()   # =
    COMMA      = auto()
    COLON      = auto()
    LPAREN     = auto()
    RPAREN     = auto()
    LBRACKET   = auto()
    RBRACKET   = auto()
    # structural
    NEWLINE    = auto()
    INDENT     = auto()
    DEDENT     = auto()
    EOF        = auto()


KEYWORDS: set[str] = {
    "load", "save", "filter", "select", "groupby", "agg", "sort", "plot",
    "engine", "as", "by", "where", "limit", "drop", "rename", "fillna",
    "describe", "show", "sum", "mean", "min", "max", "count", "std",
    "median", "ascending", "descending", "bar", "line", "scatter", "pie",
    "hist", "and", "or", "not", "in", "with", "from", "to", "using",
    "title", "xlabel", "ylabel",
}

# ordered list of (TokenType, compiled-regex) tried in sequence
TOKEN_PATTERNS: list[tuple[TokenType, re.Pattern]] = [
    (TokenType.NUMBER,     re.compile(r'-?\d+(\.\d+)?')),
    (TokenType.STRING,     re.compile(r'"[^"]*"|\'[^\']*\'')),
    (TokenType.BOOL,       re.compile(r'\b(true|false)\b')),
    (TokenType.PIPE,       re.compile(r'->')),
    (TokenType.IDENTIFIER, re.compile(r'(>=|<=|!=|==)')),   # two-char ops as IDENTIFIER
    (TokenType.IDENTIFIER, re.compile(r'[><!]')),            # single-char comparison ops
    (TokenType.ASSIGN,     re.compile(r'=')),
    (TokenType.COMMA,      re.compile(r',')),
    (TokenType.COLON,      re.compile(r':')),
    (TokenType.LPAREN,     re.compile(r'\(')),
    (TokenType.RPAREN,     re.compile(r'\)')),
    (TokenType.LBRACKET,   re.compile(r'\[')),
    (TokenType.RBRACKET,   re.compile(r'\]')),
    (TokenType.IDENTIFIER, re.compile(r'[A-Za-z_][A-Za-z0-9_]*')),
]


# ═══════════════════════════════════════════════════════════════════════════════
#  2.  TOKEN  (data carrier)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class Token:
    type:    TokenType
    value:   str
    line:    int
    column:  int

    def __repr__(self) -> str:
        return f"Token({self.type.name}, {self.value!r}, {self.line}:{self.column})"


# ═══════════════════════════════════════════════════════════════════════════════
#  3.  LEXER
# ═══════════════════════════════════════════════════════════════════════════════

class LexerError(Exception):
    pass


class Lexer:
    """Tokenises a PolarPandas DSL source string."""

    def __init__(self, source: str):
        self.source  = source
        self.pos     = 0
        self.line    = 1
        self.column  = 1
        self._indent_stack: list[int] = [0]
        self._pending: list[Token]    = []

    # ── public ────────────────────────────────────────────────────────────────

    def tokenize(self) -> list[Token]:
        tokens: list[Token] = []
        for tok in self._all_tokens():
            tokens.append(tok)
        return tokens

    # ── internals ─────────────────────────────────────────────────────────────

    def _all_tokens(self):
        lines = self.source.splitlines(keepends=True)
        line_no = 0

        for raw_line in lines:
            line_no += 1
            stripped = raw_line.rstrip('\n')

            # measure indentation
            indent = len(stripped) - len(stripped.lstrip())
            content = stripped.lstrip()

            if not content or content.startswith('#'):
                continue   # blank / comment line

            current_indent = self._indent_stack[-1]
            if indent > current_indent:
                self._indent_stack.append(indent)
                yield Token(TokenType.INDENT, '', line_no, 1)
            while indent < self._indent_stack[-1]:
                self._indent_stack.pop()
                yield Token(TokenType.DEDENT, '', line_no, 1)

            # lex the content of this line
            col = indent + 1
            pos = 0
            while pos < len(content):
                # skip whitespace
                if content[pos] == ' ':
                    pos += 1; col += 1
                    continue
                # skip inline comment
                if content[pos] == '#':
                    break

                matched = False
                for tok_type, pattern in TOKEN_PATTERNS:
                    m = pattern.match(content, pos)
                    if m:
                        value = m.group(0)
                        # promote IDENTIFIER to KEYWORD or BOOL
                        if tok_type == TokenType.IDENTIFIER:
                            if value in ('true', 'false'):
                                tok_type = TokenType.BOOL
                                value = value  # keep lowercase per spec
                            elif value in KEYWORDS:
                                tok_type = TokenType.KEYWORD
                        yield Token(tok_type, value, line_no, col)
                        col += len(value)
                        pos += len(value)
                        matched = True
                        break

                if not matched:
                    raise LexerError(
                        f"Unexpected character {content[pos]!r} "
                        f"at line {line_no}, col {col}"
                    )

            yield Token(TokenType.NEWLINE, '', line_no, col)

        # close any remaining indentation
        while len(self._indent_stack) > 1:
            self._indent_stack.pop()
            yield Token(TokenType.DEDENT, '', line_no + 1, 1)

        yield Token(TokenType.EOF, '', line_no + 1, 1)


# ═══════════════════════════════════════════════════════════════════════════════
#  4.  AST NODES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class ASTNode:
    """Base class for all AST nodes."""

# ── literals & atoms ──────────────────────────────────────────────────────────

@dataclass(frozen=True)
class NumberLiteral(ASTNode):
    value: float

@dataclass(frozen=True)
class StringLiteral(ASTNode):
    value: str

@dataclass(frozen=True)
class BoolLiteral(ASTNode):
    value: bool

@dataclass(frozen=True)
class Identifier(ASTNode):
    name: str

# ── expressions ───────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class ColumnList(ASTNode):
    """select [col1, col2, ...]"""
    columns: tuple[str, ...]

@dataclass(frozen=True)
class BinaryOp(ASTNode):
    """condition: left op right  (e.g. age > 30)"""
    left:     ASTNode
    operator: str
    right:    ASTNode

@dataclass(frozen=True)
class LogicalOp(ASTNode):
    """and / or of two sub-conditions"""
    left:     ASTNode
    operator: str   # 'and' | 'or'
    right:    ASTNode

@dataclass(frozen=True)
class NotOp(ASTNode):
    operand: ASTNode

@dataclass(frozen=True)
class AggCall(ASTNode):
    """sum(col) / mean(col) / ..."""
    function: str
    column:   str

@dataclass(frozen=True)
class KwArg(ASTNode):
    """key=value keyword argument used in plot, save, etc."""
    key:   str
    value: ASTNode

# ── pipeline steps ────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class LoadStep(ASTNode):
    path:   ASTNode          # StringLiteral
    engine: str | None       # 'pandas' | 'polars' | None

@dataclass(frozen=True)
class SaveStep(ASTNode):
    path:   ASTNode
    kwargs: tuple[KwArg, ...]

@dataclass(frozen=True)
class FilterStep(ASTNode):
    condition: ASTNode

@dataclass(frozen=True)
class SelectStep(ASTNode):
    columns: ColumnList

@dataclass(frozen=True)
class GroupByStep(ASTNode):
    columns: ColumnList

@dataclass(frozen=True)
class AggStep(ASTNode):
    aggregations: tuple[AggCall, ...]

@dataclass(frozen=True)
class SortStep(ASTNode):
    columns:   ColumnList
    direction: str   # 'ascending' | 'descending'

@dataclass(frozen=True)
class PlotStep(ASTNode):
    kind:   str   # 'bar' | 'line' | 'scatter' | 'pie' | 'hist'
    kwargs: tuple[KwArg, ...]

@dataclass(frozen=True)
class ShowStep(ASTNode):
    pass

@dataclass(frozen=True)
class DescribeStep(ASTNode):
    pass

@dataclass(frozen=True)
class LimitStep(ASTNode):
    count: int

# ── top-level ─────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class Pipeline(ASTNode):
    """One named pipeline: name = load(...) -> filter(...) -> ..."""
    name:  str | None           # None for anonymous pipelines
    steps: tuple[ASTNode, ...]

@dataclass(frozen=True)
class Program(ASTNode):
    """Root node — contains all pipelines in the source file."""
    pipelines: tuple[Pipeline, ...]


# ═══════════════════════════════════════════════════════════════════════════════
#  5.  PARSER
# ═══════════════════════════════════════════════════════════════════════════════

class ParseError(Exception):
    pass


class Parser:
    """
    Recursive-descent parser for the PolarPandas DSL.

    Grammar (informal):
        program     = pipeline* EOF
        pipeline    = [IDENTIFIER '='] step ('->' step)* NEWLINE
        step        = load | save | filter | select | groupby
                    | agg | sort | plot | show | describe | limit
        load        = 'load' '(' string [',' 'engine' '=' IDENTIFIER] ')'
        save        = 'save' '(' string [',' kwarg*] ')'
        filter      = 'filter' '(' condition ')'
        select      = 'select' '[' col_list ']'
        groupby     = 'groupby' '[' col_list ']'
        agg         = 'agg' '(' agg_call [',' agg_call]* ')'
        sort        = 'sort' '[' col_list ']' ['ascending'|'descending']
        plot        = 'plot' '(' IDENTIFIER [',' kwarg*] ')'
        show        = 'show'
        describe    = 'describe'
        limit       = 'limit' '(' NUMBER ')'
        condition   = or_expr
        or_expr     = and_expr ('or' and_expr)*
        and_expr    = not_expr ('and' not_expr)*
        not_expr    = 'not' not_expr | compare
        compare     = atom (OP atom)?
        atom        = NUMBER | STRING | BOOL | IDENTIFIER | '(' condition ')'
        agg_call    = IDENTIFIER '(' IDENTIFIER ')'
        col_list    = IDENTIFIER (',' IDENTIFIER)*
        kwarg       = IDENTIFIER '=' atom
        string      = STRING
    """

    COMPARE_OPS = {'>', '<', '>=', '<=', '==', '!=', 'in'}

    def __init__(self, tokens: list[Token]):
        self._tokens = [t for t in tokens
                        if t.type not in (TokenType.INDENT, TokenType.DEDENT)]
        self._pos = 0

    # ── helpers ───────────────────────────────────────────────────────────────

    def _peek(self, offset: int = 0) -> Token:
        idx = self._pos + offset
        if idx < len(self._tokens):
            return self._tokens[idx]
        return self._tokens[-1]  # EOF

    def _advance(self) -> Token:
        tok = self._tokens[self._pos]
        if self._pos < len(self._tokens) - 1:
            self._pos += 1
        return tok

    def _check(self, typ: TokenType, value: str | None = None) -> bool:
        tok = self._peek()
        if tok.type != typ:
            return False
        return value is None or tok.value == value

    def _match(self, typ: TokenType, value: str | None = None) -> bool:
        if self._check(typ, value):
            self._advance()
            return True
        return False

    def _expect(self, typ: TokenType, value: str | None = None) -> Token:
        tok = self._peek()
        if not self._check(typ, value):
            expected = f"{typ.name}" + (f"({value!r})" if value else "")
            raise ParseError(
                f"Line {tok.line}:{tok.column} — expected {expected}, "
                f"got {tok.type.name}({tok.value!r})"
            )
        return self._advance()

    def _skip_newlines(self):
        while self._check(TokenType.NEWLINE):
            self._advance()

    # ── grammar rules ─────────────────────────────────────────────────────────

    def parse(self) -> Program:
        self._skip_newlines()
        pipelines: list[Pipeline] = []
        while not self._check(TokenType.EOF):
            pipelines.append(self._parse_pipeline())
            self._skip_newlines()
        return Program(pipelines=tuple(pipelines))

    def _parse_pipeline(self) -> Pipeline:
        # optional  name =
        name: str | None = None
        if (self._check(TokenType.IDENTIFIER)
                and self._peek(1).type == TokenType.ASSIGN):
            name = self._advance().value
            self._advance()  # consume '='

        steps: list[ASTNode] = [self._parse_step()]
        while self._check(TokenType.PIPE):
            self._advance()
            steps.append(self._parse_step())

        # consume trailing newline(s)
        while self._check(TokenType.NEWLINE):
            self._advance()

        return Pipeline(name=name, steps=tuple(steps))

    def _parse_step(self) -> ASTNode:
        tok = self._peek()
        if tok.type != TokenType.KEYWORD:
            raise ParseError(
                f"Line {tok.line}:{tok.column} — expected a pipeline keyword, "
                f"got {tok.type.name}({tok.value!r})"
            )
        kw = tok.value
        dispatch = {
            'load':     self._parse_load,
            'save':     self._parse_save,
            'filter':   self._parse_filter,
            'select':   self._parse_select,
            'groupby':  self._parse_groupby,
            'agg':      self._parse_agg,
            'sort':     self._parse_sort,
            'plot':     self._parse_plot,
            'show':     self._parse_show,
            'describe': self._parse_describe,
            'limit':    self._parse_limit,
        }
        if kw not in dispatch:
            raise ParseError(f"Line {tok.line} — unknown step keyword {kw!r}")
        return dispatch[kw]()

    # ── step parsers ──────────────────────────────────────────────────────────

    def _parse_load(self) -> LoadStep:
        self._expect(TokenType.KEYWORD, 'load')
        self._expect(TokenType.LPAREN)
        path = self._parse_string()
        engine: str | None = None
        if self._match(TokenType.COMMA):
            self._expect(TokenType.KEYWORD, 'engine')
            self._expect(TokenType.ASSIGN)
            engine = self._expect(TokenType.IDENTIFIER).value
        self._expect(TokenType.RPAREN)
        return LoadStep(path=path, engine=engine)

    def _parse_save(self) -> SaveStep:
        self._expect(TokenType.KEYWORD, 'save')
        self._expect(TokenType.LPAREN)
        path = self._parse_string()
        kwargs: list[KwArg] = []
        while self._match(TokenType.COMMA):
            kwargs.append(self._parse_kwarg())
        self._expect(TokenType.RPAREN)
        return SaveStep(path=path, kwargs=tuple(kwargs))

    def _parse_filter(self) -> FilterStep:
        self._expect(TokenType.KEYWORD, 'filter')
        self._expect(TokenType.LPAREN)
        cond = self._parse_condition()
        self._expect(TokenType.RPAREN)
        return FilterStep(condition=cond)

    def _parse_select(self) -> SelectStep:
        self._expect(TokenType.KEYWORD, 'select')
        cols = self._parse_col_list_bracketed()
        return SelectStep(columns=cols)

    def _parse_groupby(self) -> GroupByStep:
        self._expect(TokenType.KEYWORD, 'groupby')
        cols = self._parse_col_list_bracketed()
        return GroupByStep(columns=cols)

    def _parse_agg(self) -> AggStep:
        self._expect(TokenType.KEYWORD, 'agg')
        self._expect(TokenType.LPAREN)
        calls: list[AggCall] = [self._parse_agg_call()]
        while self._match(TokenType.COMMA):
            calls.append(self._parse_agg_call())
        self._expect(TokenType.RPAREN)
        return AggStep(aggregations=tuple(calls))

    def _parse_sort(self) -> SortStep:
        self._expect(TokenType.KEYWORD, 'sort')
        cols = self._parse_col_list_bracketed()
        direction = 'ascending'
        if self._check(TokenType.KEYWORD, 'ascending'):
            self._advance(); direction = 'ascending'
        elif self._check(TokenType.KEYWORD, 'descending'):
            self._advance(); direction = 'descending'
        return SortStep(columns=cols, direction=direction)

    def _parse_plot(self) -> PlotStep:
        self._expect(TokenType.KEYWORD, 'plot')
        self._expect(TokenType.LPAREN)
        kind_tok = self._peek()
        if kind_tok.type not in (TokenType.KEYWORD, TokenType.IDENTIFIER):
            raise ParseError(f"Line {kind_tok.line} — expected plot kind")
        kind = self._advance().value
        kwargs: list[KwArg] = []
        while self._match(TokenType.COMMA):
            kwargs.append(self._parse_kwarg())
        self._expect(TokenType.RPAREN)
        return PlotStep(kind=kind, kwargs=tuple(kwargs))

    def _parse_show(self) -> ShowStep:
        self._expect(TokenType.KEYWORD, 'show')
        return ShowStep()

    def _parse_describe(self) -> DescribeStep:
        self._expect(TokenType.KEYWORD, 'describe')
        return DescribeStep()

    def _parse_limit(self) -> LimitStep:
        self._expect(TokenType.KEYWORD, 'limit')
        self._expect(TokenType.LPAREN)
        n = int(float(self._expect(TokenType.NUMBER).value))
        self._expect(TokenType.RPAREN)
        return LimitStep(count=n)

    # ── expression / condition parsers ────────────────────────────────────────

    def _parse_condition(self) -> ASTNode:
        return self._parse_or()

    def _parse_or(self) -> ASTNode:
        left = self._parse_and()
        while self._check(TokenType.KEYWORD, 'or'):
            self._advance()
            right = self._parse_and()
            left = LogicalOp(left=left, operator='or', right=right)
        return left

    def _parse_and(self) -> ASTNode:
        left = self._parse_not()
        while self._check(TokenType.KEYWORD, 'and'):
            self._advance()
            right = self._parse_not()
            left = LogicalOp(left=left, operator='and', right=right)
        return left

    def _parse_not(self) -> ASTNode:
        if self._check(TokenType.KEYWORD, 'not'):
            self._advance()
            return NotOp(operand=self._parse_not())
        return self._parse_compare()

    def _parse_compare(self) -> ASTNode:
        left = self._parse_atom()
        tok = self._peek()
        # operator can be a multi-char symbol or 'in' keyword
        op: str | None = None
        if tok.type == TokenType.KEYWORD and tok.value == 'in':
            op = 'in'
        elif tok.type == TokenType.IDENTIFIER and tok.value in self.COMPARE_OPS:
            op = tok.value
        elif tok.type == TokenType.ASSIGN:   # bare '='  treat as '=='
            op = '=='
        else:
            # check for two-char ops tokenised as two single-char tokens
            raw = tok.value
            if raw in ('>', '<', '!'):
                nxt = self._peek(1).value
                if nxt == '=':
                    op = raw + '='

        if op is not None:
            # consume the operator token(s)
            self._advance()
            if len(op) == 2 and self._check(TokenType.ASSIGN):
                self._advance()
            right = self._parse_atom()
            return BinaryOp(left=left, operator=op, right=right)
        return left

    def _parse_atom(self) -> ASTNode:
        tok = self._peek()
        if tok.type == TokenType.NUMBER:
            self._advance()
            return NumberLiteral(value=float(tok.value))
        if tok.type == TokenType.STRING:
            self._advance()
            return StringLiteral(value=tok.value.strip('"\''))
        if tok.type == TokenType.BOOL:
            self._advance()
            return BoolLiteral(value=(tok.value == 'true'))
        if tok.type == TokenType.IDENTIFIER:
            self._advance()
            return Identifier(name=tok.value)
        if tok.type == TokenType.KEYWORD:
            # keyword used as column name (e.g. 'count' as identifier)
            self._advance()
            return Identifier(name=tok.value)
        if tok.type == TokenType.LPAREN:
            self._advance()
            expr = self._parse_condition()
            self._expect(TokenType.RPAREN)
            return expr
        raise ParseError(
            f"Line {tok.line}:{tok.column} — unexpected token "
            f"{tok.type.name}({tok.value!r}) in expression"
        )

    # ── sub-structure parsers ─────────────────────────────────────────────────

    def _parse_col_list_bracketed(self) -> ColumnList:
        self._expect(TokenType.LBRACKET)
        cols = self._parse_col_list()
        self._expect(TokenType.RBRACKET)
        return cols

    def _parse_col_list(self) -> ColumnList:
        cols: list[str] = []
        tok = self._peek()
        if tok.type in (TokenType.IDENTIFIER, TokenType.KEYWORD):
            cols.append(self._advance().value)
        while self._match(TokenType.COMMA):
            tok = self._peek()
            if tok.type in (TokenType.IDENTIFIER, TokenType.KEYWORD):
                cols.append(self._advance().value)
        return ColumnList(columns=tuple(cols))

    def _parse_agg_call(self) -> AggCall:
        fn_tok = self._peek()
        if fn_tok.type not in (TokenType.KEYWORD, TokenType.IDENTIFIER):
            raise ParseError(f"Line {fn_tok.line} — expected aggregation function")
        fn = self._advance().value
        self._expect(TokenType.LPAREN)
        col = self._expect(TokenType.IDENTIFIER).value
        self._expect(TokenType.RPAREN)
        return AggCall(function=fn, column=col)

    def _parse_kwarg(self) -> KwArg:
        key_tok = self._peek()
        if key_tok.type not in (TokenType.IDENTIFIER, TokenType.KEYWORD):
            raise ParseError(f"Line {key_tok.line} — expected keyword argument name")
        key = self._advance().value
        self._expect(TokenType.ASSIGN)
        value = self._parse_atom()
        return KwArg(key=key, value=value)

    def _parse_string(self) -> StringLiteral:
        tok = self._expect(TokenType.STRING)
        return StringLiteral(value=tok.value.strip('"\''))


# ═══════════════════════════════════════════════════════════════════════════════
#  6.  AST PRETTY-PRINTER
# ═══════════════════════════════════════════════════════════════════════════════

def print_ast(node: ASTNode, indent: int = 0) -> None:
    pad  = "  " * indent
    pad2 = "  " * (indent + 1)

    match node:
        case Program(pipelines=pl):
            print(f"{pad}Program")
            for p in pl:
                print_ast(p, indent + 1)

        case Pipeline(name=n, steps=st):
            label = f" [{n}]" if n else " [anonymous]"
            print(f"{pad}Pipeline{label}")
            for s in st:
                print_ast(s, indent + 1)

        case LoadStep(path=p, engine=e):
            print(f"{pad}LoadStep  engine={e or 'default'}")
            print_ast(p, indent + 1)

        case SaveStep(path=p, kwargs=kw):
            print(f"{pad}SaveStep")
            print_ast(p, indent + 1)
            for k in kw:
                print_ast(k, indent + 1)

        case FilterStep(condition=c):
            print(f"{pad}FilterStep")
            print_ast(c, indent + 1)

        case SelectStep(columns=c):
            print(f"{pad}SelectStep  cols={list(c.columns)}")

        case GroupByStep(columns=c):
            print(f"{pad}GroupByStep  cols={list(c.columns)}")

        case AggStep(aggregations=aggs):
            print(f"{pad}AggStep")
            for a in aggs:
                print(f"{pad2}AggCall  {a.function}({a.column})")

        case SortStep(columns=c, direction=d):
            print(f"{pad}SortStep  {d}  cols={list(c.columns)}")

        case PlotStep(kind=k, kwargs=kw):
            print(f"{pad}PlotStep  kind={k}")
            for kwarg in kw:
                print_ast(kwarg, indent + 1)

        case ShowStep():
            print(f"{pad}ShowStep")

        case DescribeStep():
            print(f"{pad}DescribeStep")

        case LimitStep(count=n):
            print(f"{pad}LimitStep  n={n}")

        case BinaryOp(left=l, operator=op, right=r):
            print(f"{pad}BinaryOp  op={op!r}")
            print_ast(l, indent + 1)
            print_ast(r, indent + 1)

        case LogicalOp(left=l, operator=op, right=r):
            print(f"{pad}LogicalOp  op={op!r}")
            print_ast(l, indent + 1)
            print_ast(r, indent + 1)

        case NotOp(operand=o):
            print(f"{pad}NotOp")
            print_ast(o, indent + 1)

        case KwArg(key=k, value=v):
            print(f"{pad}KwArg  key={k!r}")
            print_ast(v, indent + 1)

        case NumberLiteral(value=v):
            print(f"{pad}Number({v})")

        case StringLiteral(value=v):
            print(f"{pad}String({v!r})")

        case BoolLiteral(value=v):
            print(f"{pad}Bool({v})")

        case Identifier(name=n):
            print(f"{pad}Identifier({n!r})")

        case ColumnList(columns=c):
            print(f"{pad}ColumnList{list(c)}")

        case _:
            print(f"{pad}{node!r}")


# ═══════════════════════════════════════════════════════════════════════════════
#  7.  DEMO
# ═══════════════════════════════════════════════════════════════════════════════

SAMPLE = """\
# Simple load + show
result = load("data/sales.csv") -> filter(region == "EU") -> select[region, revenue, units] -> sort[revenue] descending -> limit(10) -> show

# Aggregation pipeline
summary = load("data/sales.csv", engine=polars) -> filter(revenue > 1000 and not region == "US") -> groupby[region] -> agg(sum(revenue), mean(units)) -> sort[revenue] descending -> plot(bar, title="Revenue by Region", xlabel="Region", ylabel="Revenue") -> save("output/summary.csv")
"""


def main():
    print("=" * 65)
    print(" PolarPandas DSL  —  Lexer + Parser Demo")
    print("=" * 65)

    # ── lex ──────────────────────────────────────────────────────────
    print("\n── TOKENS ─────────────────────────────────────────────────\n")
    lexer  = Lexer(SAMPLE)
    tokens = lexer.tokenize()
    for tok in tokens:
        if tok.type not in (TokenType.NEWLINE, TokenType.EOF):
            print(f"  {tok}")

    # ── parse ─────────────────────────────────────────────────────────
    print("\n── AST ────────────────────────────────────────────────────\n")
    parser = Parser(tokens)
    ast    = parser.parse()
    print_ast(ast)

    print("\n── DONE  (no errors) ──────────────────────────────────────")


if __name__ == "__main__":
    main()