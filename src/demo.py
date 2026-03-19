"""
demo.py — runs the lexer against several example inputs and prints results.
"""

from lexer import Lexer, LexError


EXAMPLES = [
    # Basic arithmetic
    ("Arithmetic",          "(+ 1 2)"),
    # Nested expression
    ("Nested ops",          "(* (+ 3 4) (- 10 2.5))"),
    # Trig with named constant
    ("Trig + constant",     "(sin (* pi 0.5))"),
    # Multiple trig functions
    ("Multi-trig",          "(+ (cos 0) (tan (/ pi 4)))"),
    # Float literals
    ("Float literals",      "(* 1.5e2 .75)"),
    # Variable definition
    ("define",              "(define radius 6.371e3)"),
    # Let binding
    ("let binding",         "(let ((x 3) (y 4)) (^ (+ (* x x) (* y y)) 0.5))"),
    # Euler's number
    ("Euler constant",      "(* e 2.718)"),
    # Inline comment
    ("Comment skipping",    "; circumference formula\n(* 2 pi radius)"),
    # Error case
    ("Error: bad char",     "(+ 1 @2)"),
]


def run_demo():
    for title, source in EXAMPLES:
        print(f"\n{'─'*60}")
        print(f"  {title}")
        print(f"  Source : {source!r}")
        print(f"{'─'*60}")
        try:
            tokens = Lexer(source).tokenize()
            for tok in tokens:
                print(f"    {tok}")
        except LexError as err:
            print(f"    !! LexError: {err}")


if __name__ == "__main__":
    run_demo()