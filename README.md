# Lab 5 — Chomsky Normal Form

**Course:** Formal Languages & Finite Automata  
**Author:** \<your name\>  
**Group:** FAF-241  
**Variant:** 15  

---

## Theory

A **Context-Free Grammar (CFG)** is a 4-tuple G = (V_N, V_T, P, S) where V_N is a set of non-terminals, V_T a set of terminals, P a set of production rules A → α, and S the start symbol.

**Chomsky Normal Form (CNF)** restricts every production to one of two shapes:

```
A → BC      (exactly two non-terminals)
A → a       (exactly one terminal)
```

Any context-free language except {ε} can be expressed this way. CNF is the prerequisite for the CYK parsing algorithm (O(n³)) and simplifies most proofs about CFLs.

Conversion from an arbitrary CFG to CNF follows five steps, applied in order:

| # | Step | What it removes |
|---|---|---|
| 1 | Eliminate ε-productions | Rules of the form A → ε |
| 2 | Eliminate unit rules | Rules of the form A → B |
| 3 | Eliminate inaccessible symbols | Non-terminals unreachable from S |
| 4 | Eliminate non-productive symbols | Non-terminals that can't derive any terminal string |
| 5 | Binarize | Long RHS and mixed terminal/non-terminal RHS |

---

## Objectives

1. Understand CNF and why it is useful.
2. Implement each normalization step as a standalone method.
3. Encapsulate everything in a reusable `Grammar` class that accepts **any** CFG as input.
4. Verify the result programmatically using an `is_cnf()` validator.

---

## Implementation

The entire solution lives in `main.py` — no external dependencies, just the standard library.

### Grammar class

```python
class Grammar:
    def __init__(self, variables, terminals, productions, start): ...
```

Productions are stored as `dict[str, list[list[str]]]`. Each non-terminal maps to a list of alternative RHS sequences, where each RHS is a list of symbol strings. The empty string `""` represents ε.

```python
cnf = grammar.normalize()   # chains all 5 steps, prints each intermediate result
cnf.is_cnf()                # → True / False
```

Each step is also independently callable, which keeps the logic auditable and testable in isolation.

---

### Step 1 — `eliminate_epsilon()`

Computes the **nullable set** (variables that can derive ε, directly or via a chain) through a fixed-point loop. For every production, every subset of nullable positions is enumerated and a new production is emitted for each non-empty combination. All ε-rules are then removed.

For Variant 15, `A → ε` makes A nullable. Compensating rules produced include `S → b` (from `S → bA`), `S → C` (from `S → AC`), and `D → B` (from `D → AB`).

---

### Step 2 — `eliminate_unit_rules()`

Computes the reflexive-transitive closure of **unit pairs** `{(A, B) | A ⇒* B via single-variable rules}`. For each pair (A, B), all non-unit productions of B are copied directly into A. Unit rules are then discarded.

`S → B` is a unit rule in the grammar after step 1. S therefore inherits `B → a` and `B → bS` directly.

---

### Step 3 — `eliminate_inaccessible()`

BFS from the start symbol through every reachable production's right-hand side. Any non-terminal never visited — along with all its rules — is removed.

After steps 1–2, `D` is referenced by no rule reachable from S. It is dropped here.

---

### Step 4 — `eliminate_non_productive()`

Iteratively marks variables **productive** if they have at least one production whose symbols are all terminals or previously-marked productive variables. Variables that never become productive — together with every production referencing them — are removed.

`C → abC` has no terminal base case: C recurses into itself forever and can never fully reduce. C is non-productive and removed, which also eliminates `S → AC` and `S → abC`.

---

### Step 5 — `to_cnf()`

Two sub-tasks:

1. **Terminal proxies** — for each terminal `t`, a fresh variable `T_ → t` is introduced. Every occurrence of `t` inside a production of length ≥ 2 is replaced by `T_`.
2. **Binarization** — any RHS of length > 2 is right-folded: the last two symbols are collected into a fresh chain variable `Zn → Y₁ Y₂`, shrinking the RHS by one. This repeats until every RHS has length exactly 2.

---

## Variant 15 — Walkthrough

Starting grammar:

```
G = ({S, A, B, C, D}, {a, b}, P, S)

S → AC | bA | B | aA
A → ε  | aS | ABab
B → a  | bS
C → abC
D → AB
```

---

**After Step 1 — ε eliminated**

A is nullable. Every production containing A gets variants with A present and absent.

```
A → aS | ABab | Bab
B → a  | bS
C → abC
D → AB | B
S → AC | C | bA | b | B | aA | a
```

---

**After Step 2 — Unit rules eliminated**

`S → B`, `S → C`, `D → B` are unit rules. Each is replaced by the non-unit productions of its target.

```
A → aS | ABab | Bab
B → a  | bS
C → abC
D → AB | a | bS
S → AC | bA | b | aA | a | bS | abC
```

---

**After Step 3 — Inaccessible symbols removed**

`D` has no references in any rule reachable from S → removed.

```
Variables: {S, A, B, C}
```

---

**After Step 4 — Non-productive symbols removed**

`C → abC` never terminates (no base case) → C is non-productive → removed.  
`S → AC` and `S → abC` are also dropped.

```
Variables: {S, A, B}

A → aS | ABab | Bab
B → a  | bS
S → bA | b | aA | a | bS
```

---

**After Step 5 — CNF**

Terminal proxies: `A_0 → a`, `B_1 → b`.  
Long productions folded right-to-left:

```
A → ABab   →   A → A Z3,   Z3 → B Z2,   Z2 → A_0 B_1
A → Bab    →   A → B Z4,   Z4 → A_0 B_1
```

Final CNF grammar:

```
A_0  →  a
B_1  →  b
Z2   →  A_0 B_1
Z3   →  B Z2
Z4   →  A_0 B_1
A    →  A_0 S  |  A Z3  |  B Z4
B    →  a  |  B_1 S
S    →  B_1 A  |  b  |  A_0 A  |  a  |  B_1 S
```

`is_cnf() → True` ✅

---

## Results

| After step | Variables |
|---|---|
| Original | S, A, B, C, D |
| 1 — ε removed | S, A, B, C, D |
| 2 — unit rules removed | S, A, B, C, D |
| 3 — inaccessible removed | S, A, B, C |
| 4 — non-productive removed | S, A, B |
| 5 — CNF | S, A, B, A_0, B_1, Z2, Z3, Z4 |

The grammar went from 5 variables and 11 productions to 8 variables and 13 productions, all satisfying CNF constraints.

---

## Conclusions

- **Nullable propagation** is the most subtle step: when A is nullable in `ABab`, the compensating rules are `Bab` (A omitted) and `ABab` (A kept) — not just a deletion.
- **Order is mandatory.** Eliminating inaccessible symbols before unit rules can incorrectly retain variables that only become inaccessible after unit inlining is complete.
- **C was always doomed.** `C → abC` looks productive at first glance but has no terminal base case. Recognizing non-productivity requires the fixed-point algorithm, not visual inspection.
- **D became irrelevant.** It was never non-productive — it simply lost all references once the grammar was cleaned up around it.
- **Binarization is mechanical** but introduces O(n) helper variables per long production. Right-folding is chosen here because it produces a right-branching parse tree, which is the conventional approach.
- The `Grammar` class is fully generic: any CFG can be passed in and `normalize()` will produce a valid CNF, satisfying the bonus requirement.