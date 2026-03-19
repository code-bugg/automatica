# Laboratory Works 1 & 2: Formal Languages & Finite Automata

**Course:** Formal Languages & Finite Automata  
**Author:** *(your name)*  
**Variant:** 15  
**Kudos to:** Vasile Drumea and Irina Cojuhari

---

## Table of Contents

1. [Theory](#theory)
2. [Objectives](#objectives)
3. [Variant 15 Grammar](#variant-15-grammar)
4. [Project Structure](#project-structure)
5. [Implementation](#implementation)
   - [Grammar Class](#grammar-class)
   - [FiniteAutomaton Class](#finiteautomaton-class)
6. [Results](#results)
   - [Grammar Classification](#grammar-classification)
   - [String Generation](#string-generation)
   - [Grammar to FA Conversion](#grammar-to-fa-conversion)
   - [Determinism Check](#determinism-check)
   - [FA to Regular Grammar](#fa-to-regular-grammar)
   - [Subset Construction — NDFA to DFA](#subset-construction--ndfa-to-dfa)
   - [Formal Verification](#formal-verification)
   - [Additional NDFA Test Case](#additional-ndfa-test-case)
7. [Conclusions](#conclusions)
8. [References](#references)

---

## Theory

### Formal Grammars

A **formal grammar** is a 4-tuple $G = (V_N, V_T, P, S)$ where:

| Component | Description |
|-----------|-------------|
| $V_N$ | Finite set of **non-terminal** symbols (variables) |
| $V_T$ | Finite set of **terminal** symbols (the actual alphabet) |
| $P$ | Finite set of **production rules** of the form $\alpha \rightarrow \beta$ |
| $S \in V_N$ | The **start symbol** |

Noam Chomsky classified grammars into four types based on the shape of their production rules:

| Type | Name | LHS constraint | RHS constraint |
|------|------|---------------|----------------|
| 0 | Unrestricted | Any string | Any string |
| 1 | Context-sensitive | $\alpha A \beta \rightarrow \alpha \gamma \beta$ | $|\text{RHS}| \geq |\text{LHS}|$ |
| 2 | Context-free | Single non-terminal $A$ | Any string |
| 3 | Regular | Single non-terminal $A$ | $aB$ or $a$ (right-linear) OR $Ba$ or $a$ (left-linear) |

Each type is a strict subset of the one above: every regular grammar is also context-free, and so on.

### Finite Automata

A **Finite Automaton** is a 5-tuple $M = (Q, \Sigma, \delta, q_0, F)$ where:

| Component | Description |
|-----------|-------------|
| $Q$ | Finite set of states |
| $\Sigma$ | Input alphabet |
| $\delta: Q \times \Sigma \rightarrow 2^Q$ | Transition function |
| $q_0 \in Q$ | Start state |
| $F \subseteq Q$ | Set of accepting (final) states |

A FA is **deterministic (DFA)** if $\delta(q, a)$ returns exactly one state for every $(q, a)$ pair. If any pair returns more than one state, or a state has no transition for some symbol, the FA is **non-deterministic (NDFA)**.

**Key theorem:** Every NDFA has an equivalent DFA that recognises the same language. The **Subset Construction algorithm** converts an NDFA to a DFA by treating *sets of NDFA states* as single DFA states.

**Connection between Type 3 grammars and FA:** Every regular grammar generates a regular language that can be recognised by a finite automaton, and vice versa. The mapping is direct: a right-linear rule $A \rightarrow aB$ becomes the transition $\delta(A, a) = B$, and a terminating rule $A \rightarrow a$ becomes $\delta(A, a) = X$ where $X$ is an accepting state.

---

## Objectives

### Laboratory Work 1
- Implement a `Grammar` class representing $G = (V_N, V_T, P, S)$.
- Generate terminal strings by repeatedly applying production rules from $S$.
- Convert a regular grammar into its equivalent Finite Automaton.

### Laboratory Work 2
- Implement Chomsky classification (Type 0–3) for any grammar.
- Determine whether a given FA is deterministic or non-deterministic.
- Implement the Subset Construction algorithm to convert NDFA → DFA.
- Convert an FA back into a right-linear regular grammar.

---

## Variant 15 Grammar

$$G = (\{S, A, B\},\ \{a, b, c\},\ P,\ S)$$

Production rules $P$:

$$S \rightarrow aS \mid bS \mid cA$$
$$A \rightarrow aB$$
$$B \rightarrow aB \mid bB \mid c$$

**Intuition behind the language:** Any string in $L(G)$ consists of an arbitrary prefix of `a`s and `b`s, followed by exactly one `c` (which triggers the transition $S \rightarrow cA$), followed by one or more `a`s and `b`s, followed by a terminating `c`. In regular expression terms:

$$L(G) = (a|b)^* \cdot c \cdot (a|b)^* \cdot c$$

Examples of strings in the language: `caac`, `bbbcac`, `aacabac`, `cbc`.  
Examples of strings **not** in the language: `abc` (no final `c` after middle `c`), `aaaac` (only one `c`).

---

## Project Structure

```
.
└── main.py    # All logic: Grammar and FiniteAutomaton classes + main runner
```

The entire implementation lives in `main.py`, which defines two classes and a `__main__` block that exercises every feature in sequence.

---

## Implementation

### Grammar Class

**Constructor**

```python
class Grammar:
    def __init__(self, V_n: set[str], V_t: set[str], P: dict[str, list[str]], S: str):
        self.V_n = V_n   # non-terminals
        self.V_t = V_t   # terminals
        self.P   = P     # production rules: {lhs: [rhs, ...]}
        self.S   = S     # start symbol
```

Productions are stored as a dictionary mapping each non-terminal string to a list of right-hand side strings, e.g. `{"S": ["aS", "bS", "cA"], "A": ["aB"], "B": ["aB", "bB", "c"]}`.

---

#### `generate_string() -> str`

Derives a terminal string from the start symbol by iteratively replacing the leftmost non-terminal with a randomly chosen production rule.

```python
def generate_string(self) -> str:
    language_string = self.S
    while not self.is_terminal(language_string):
        available_non_terminals = [char for char in language_string if char in self.V_n]
        if not available_non_terminals:
            break
        target = available_non_terminals[0]       # leftmost non-terminal
        if target in self.P:
            replacement = random.choice(self.P[target])
            language_string = language_string.replace(target, replacement, 1)
    return language_string
```

The helper `is_terminal(state)` returns `True` when no character in the string is a member of $V_N$:

```python
def is_terminal(self, state: str) -> bool:
    return all(char not in self.V_n for char in state)
```

**Example derivation** for `caac`:

$$S \xrightarrow{cA} cA \xrightarrow{aB} caB \xrightarrow{aB} caaB \xrightarrow{c} caac$$

---

#### `classify() -> str`

Determines the Chomsky type of the grammar by applying four increasingly permissive tests in order from most restrictive (Type 3) to least restrictive (Type 0). The first test that passes determines the classification.

```python
def classify(self) -> str:
    if self._is_type3(): return "Type 3 (regular)"
    if self._is_type2(): return "Type 2 (context-free)"
    if self._is_type1(): return "Type 1 (context-sensitive)"
    return "Type 0 (unrestricted)"
```

**`_is_type3()`** — checks for right-linear or left-linear rules. Every production must be of the form $A \rightarrow a$ or $A \rightarrow aB$ (right-linear), or $A \rightarrow a$ or $A \rightarrow Ba$ (left-linear). The check is applied simultaneously — a grammar is Type 3 if it is *entirely* right-linear or *entirely* left-linear:

```python
def _is_type3(self) -> bool:
    right_linear = True
    left_linear  = True
    for lhs, productions in self.P.items():
        if lhs not in self.V_n or len(lhs) != 1:
            right_linear = left_linear = False
            break
        for rhs in productions:
            is_rl = ((len(rhs) == 1 and rhs in self.V_t) or
                     (len(rhs) == 2 and rhs[0] in self.V_t and rhs[1] in self.V_n))
            is_ll = ((len(rhs) == 1 and rhs in self.V_t) or
                     (len(rhs) == 2 and rhs[0] in self.V_n and rhs[1] in self.V_t))
            if not is_rl: right_linear = False
            if not is_ll: left_linear  = False
    return right_linear or left_linear
```

**`_is_type2()`** — every LHS must be a single non-terminal (the only relaxation over Type 3 is that the RHS can be any string):

```python
def _is_type2(self) -> bool:
    for lhs in self.P:
        if len(lhs) != 1 or lhs not in self.V_n:
            return False
    return True
```

**`_is_type1()`** — no production may shrink the string ($|\text{RHS}| \geq |\text{LHS}|$), with an exception for $S \rightarrow \varepsilon$ when $S$ does not appear on any RHS:

```python
def _is_type1(self) -> bool:
    for lhs, productions in self.P.items():
        for rhs in productions:
            if rhs in ('', 'epsilon'):
                if lhs == self.S and all(lhs not in r
                        for rules in self.P.values() for r in rules):
                    continue
                return False
            if len(lhs) > len(rhs):
                return False
    return True
```

---

#### `to_finite_automaton() -> FiniteAutomaton`

Constructs a FA from the grammar using the standard right-linear grammar → FA mapping:

- States $Q = V_N \cup \{X\}$, where $X$ is a synthetic accepting state.
- $\Sigma = V_T$, start state $q_0 = S$, $F = \{X\}$.
- Rule $A \rightarrow aB$ (two-character RHS) → transition $\delta(A, a) = B$.
- Rule $A \rightarrow a$ (single terminal) → transition $\delta(A, a) = X$ (accepting).

```python
def to_finite_automaton(self):
    Q     = self.V_n | {'X'}
    Sigma = self.V_t
    q0    = self.S
    delta = {}
    F     = {'X'}

    for state, rules in self.P.items():
        for rule in rules:
            if len(rule) == 2 and rule[0] in Sigma and rule[1] in self.V_n:
                terminal, next_state = rule[0], rule[1]
                delta.setdefault((state, terminal), []).append(next_state)
            elif len(rule) == 1 and rule in Sigma:
                terminal = rule
                delta.setdefault((state, terminal), []).append('X')

    return FiniteAutomaton(Q, Sigma, delta, q0, F)
```

---

### FiniteAutomaton Class

**Constructor**

```python
class FiniteAutomaton:
    def __init__(self, Q, Sigma, delta, q0, F):
        self.Q     = Q      # set of states
        self.Sigma = Sigma  # alphabet
        self.delta = delta  # dict: (state, symbol) -> list[state]
        self.q0    = q0     # start state
        self.F     = F      # set of accepting states
```

---

#### `is_deterministic() -> bool`

A FA is non-deterministic if and only if any transition maps to more than one state. The check is O(|δ|):

```python
def is_deterministic(self) -> bool:
    for targets in self.delta.values():
        if len(targets) > 1:
            return False
    return True
```

---

#### `string_belong_to_language(input_string) -> bool`

Simulates the FA on an input string using a *set of current states* to handle both DFA and NDFA uniformly. At each step the set of reachable states is updated by following all applicable transitions:

```python
def string_belong_to_language(self, input_string: str) -> bool:
    current_states = {self.q0}
    for char in input_string:
        next_states = set()
        for state in current_states:
            if (state, char) in self.delta:
                next_states.update(self.delta[(state, char)])
        current_states = next_states
        if not current_states:
            return False
    return any(state in self.F for state in current_states)
```

The string is accepted if and only if at least one state in the final set is an accepting state.

---

#### `to_regular_grammar() -> Grammar`

Reverses the grammar → FA mapping. For each transition $\delta(q, a) = t$:

- If $t$ is a final state: add the terminal-only production $q \rightarrow a$.
- Always add the rule $q \rightarrow at$ (the next-state production).

Duplicates are removed by passing through `dict.fromkeys`:

```python
def to_regular_grammar(self) -> Grammar:
    V_n = set(self.Q)
    V_t = set(self.Sigma)
    P   = defaultdict(list)

    for (state, symbol), targets in self.delta.items():
        for t in targets:
            if t in self.F:
                P[state].append(symbol)        # terminal production
            P[state].append(symbol + t)        # recursive production

    P = {k: list(dict.fromkeys(v)) for k, v in P.items()}
    return Grammar(V_n, V_t, dict(P), self.q0)
```

---

#### `to_dfa() -> FiniteAutomaton`

Implements the **Subset Construction (Powerset Construction) algorithm**:

1. The start state of the DFA is $\{q_0\}$ — a frozenset containing the single NDFA start state.
2. For each unvisited DFA state (a frozenset of NDFA states) and each input symbol, compute the set of all NDFA states reachable via that symbol from any state in the current set. This reachable set becomes a new DFA state.
3. A DFA state is accepting if it contains at least one NDFA accepting state.
4. State names are formed by joining the sorted NDFA state names with `_` (e.g. `q0_q1`).

```python
def to_dfa(self) -> 'FiniteAutomaton':
    start     = frozenset({self.q0})
    dfa_delta = {}
    unvisited = [start]
    visited   = {start}

    while unvisited:
        current = unvisited.pop()
        for symbol in self.Sigma:
            reachable = set()
            for state in current:
                reachable.update(self.delta.get((state, symbol), []))
            target = frozenset(reachable)
            if not target:
                continue
            dfa_delta[(current, symbol)] = [target]
            if target not in visited:
                visited.add(target)
                unvisited.append(target)

    dfa_F = {s for s in visited if s & self.F}

    def name(fs):
        return '_'.join(sorted(fs)) if fs else 'DEAD'

    renamed_delta = {
        (name(src), sym): [name(tgt)]
        for (src, sym), [tgt] in dfa_delta.items()
    }

    return FiniteAutomaton(
        Q     = {name(s) for s in visited},
        Sigma = self.Sigma,
        delta = renamed_delta,
        q0    = name(start),
        F     = {name(s) for s in dfa_F}
    )
```

The worst-case complexity of subset construction is $O(2^{|Q|})$ states — exponential in the number of NDFA states. In practice, many subsets are unreachable and the actual DFA is often much smaller.

---

## Results

### Grammar Classification

```
Grammar type verification: Type 3 (regular)
```

**Why Type 3?** Every production in Variant 15 satisfies the right-linear constraint:

| Production | Form | Right-linear? |
|-----------|------|:---:|
| $S \rightarrow aS$ | $A \rightarrow aB$ | ✓ |
| $S \rightarrow bS$ | $A \rightarrow aB$ | ✓ |
| $S \rightarrow cA$ | $A \rightarrow aB$ | ✓ |
| $A \rightarrow aB$ | $A \rightarrow aB$ | ✓ |
| $B \rightarrow aB$ | $A \rightarrow aB$ | ✓ |
| $B \rightarrow bB$ | $A \rightarrow aB$ | ✓ |
| $B \rightarrow c$  | $A \rightarrow a$  | ✓ |

All rules are right-linear — the grammar is Type 3 (Regular).

---

### String Generation

Five strings generated from $S$ (random seed 42):

```
'caac'
'baaacac'
'cac'
'baaaaacac'
'acaabc'
```

**Derivation trace for `caac`:**

$$S \xrightarrow{cA} cA \xrightarrow{aB} caB \xrightarrow{aB} caaB \xrightarrow{c} caac$$

**Derivation trace for `baaacac`:**

$$S \xrightarrow{bS} bS \xrightarrow{aS} baS \xrightarrow{aS} baaS \xrightarrow{cA} baacA \xrightarrow{aB} baacaB \xrightarrow{c} baacac$$

Wait — `baaacac` has three `a`s before the first `c`. Full trace:

$$S \Rightarrow bS \Rightarrow baS \Rightarrow baaS \Rightarrow baaaS \Rightarrow baaacA \Rightarrow baaacaB \Rightarrow baaacac$$

---

### Grammar to FA Conversion

The FA produced by `grammar.to_finite_automaton()`:

```
States (Q)       : ['A', 'B', 'S', 'X']
Alphabet (Sigma) : ['a', 'b', 'c']
Start state (q0) : S
Final states (F) : ['X']
Transitions:
  delta(A, a) = ['B']
  delta(B, a) = ['B']
  delta(B, b) = ['B']
  delta(B, c) = ['X']
  delta(S, a) = ['S']
  delta(S, b) = ['S']
  delta(S, c) = ['A']
```

**Mapping summary:**

| Production | Transition |
|-----------|-----------|
| $S \rightarrow aS$ | $\delta(S, a) = S$ |
| $S \rightarrow bS$ | $\delta(S, b) = S$ |
| $S \rightarrow cA$ | $\delta(S, c) = A$ |
| $A \rightarrow aB$ | $\delta(A, a) = B$ |
| $B \rightarrow aB$ | $\delta(B, a) = B$ |
| $B \rightarrow bB$ | $\delta(B, b) = B$ |
| $B \rightarrow c$  | $\delta(B, c) = X$ (accepting) |

State `X` is a synthetic accepting state representing "string fully consumed by a terminal rule."

---

### Determinism Check

```
FA is DETERMINISTIC (DFA)
```

Every state-symbol pair in the transition table maps to exactly one target state — no ambiguity exists. `is_deterministic()` confirms this by checking that no entry in `delta` has more than one target.

---

### FA to Regular Grammar

`fa.to_regular_grammar()` reconstructs a right-linear grammar from the FA transitions:

```
Non-terminals : ['A', 'B', 'S', 'X']
Terminals     : ['a', 'b', 'c']
Start symbol  : S
Productions:
  A -> aB
  B -> aB | bB | c | cX
  S -> aS | bS | cA
```

Note that `B -> cX` appears alongside `B -> c` because the method emits both a terminal production (when the target is a final state) *and* the recursive production (always). The `B -> cX` rule is semantically equivalent — `X` is a final state so both rules accept — but it results in a slightly redundant grammar. This is a known characteristic of the reverse mapping: the reconstructed grammar is not guaranteed to be minimal.

---

### Subset Construction — NDFA to DFA

Since the Variant 15 FA is already a DFA, the subset construction simply re-maps the existing states without creating new composite states:

```
States (Q)       : ['A', 'B', 'S', 'X']
Alphabet (Sigma) : ['a', 'b', 'c']
Start state (q0) : S
Final states (F) : ['X']
Transitions:
  delta(A, a) = ['B']
  delta(B, a) = ['B']
  delta(B, b) = ['B']
  delta(B, c) = ['X']
  delta(S, a) = ['S']
  delta(S, b) = ['S']
  delta(S, c) = ['A']
DFA is deterministic: True
```

The structure is identical to the original FA, confirming that the algorithm is correct when applied to an already-deterministic automaton.

---

### Formal Verification

Six words are tested against both the original NDFA (Variant 15 FA) and the converted DFA. All results agree:

| Word | In $L(G)$? | NDFA result | DFA result | Match |
|------|:----------:|:-----------:|:----------:|:-----:|
| `caac` | Yes — $c \cdot a \cdot ac$ | `True` | `True` | ✓ |
| `aacabac` | Yes — $aa \cdot c \cdot ab \cdot ac$ | `True` | `True` | ✓ |
| `abc` | No — no second `c` | `False` | `False` | ✓ |
| `bbbcac` | Yes — $bbb \cdot c \cdot ac$ | `True` | `True` | ✓ |
| `cbac` | No — second group `ba` ends without `c` via valid path | `False` | `False` | ✓ |
| `aaaac` | No — only one `c`, at end | `False` | `False` | ✓ |

All six NDFA and DFA results are identical. This confirms that the subset construction preserved the language.

---

### Additional NDFA Test Case

A hand-crafted NDFA with genuine non-determinism is used to demonstrate the subset construction converting a true NDFA into a DFA.

**Input NDFA:**

```
States (Q)       : ['q0', 'q1', 'q2']
Alphabet (Sigma) : ['a', 'b']
Start state (q0) : q0
Final states (F) : ['q2']
Transitions:
  delta(q0, a) = ['q0', 'q1']    ← non-deterministic: two targets
  delta(q0, b) = ['q0']
  delta(q1, b) = ['q2']
is_deterministic: False
```

The state `q0` has two targets for input `a`, making this a genuine NDFA. The language accepted is: strings over `{a, b}` that end with `ab`.

**Subset Construction trace:**

| DFA state | Corresponding NDFA states | On `a` | On `b` |
|-----------|--------------------------|--------|--------|
| `q0` | $\{q_0\}$ | $\{q_0, q_1\}$ → `q0_q1` | $\{q_0\}$ → `q0` |
| `q0_q1` | $\{q_0, q_1\}$ | $\{q_0, q_1\}$ → `q0_q1` | $\{q_0, q_2\}$ → `q0_q2` ★ |
| `q0_q2` | $\{q_0, q_2\}$ | $\{q_0, q_1\}$ → `q0_q1` | $\{q_0\}$ → `q0` |

★ `q0_q2` is accepting because it contains $q_2 \in F$.

**Resulting DFA:**

```
States (Q)       : ['q0', 'q0_q1', 'q0_q2']
Alphabet (Sigma) : ['a', 'b']
Start state (q0) : q0
Final states (F) : ['q0_q2']
Transitions:
  delta(q0,     a) = ['q0_q1']
  delta(q0,     b) = ['q0']
  delta(q0_q1,  a) = ['q0_q1']
  delta(q0_q1,  b) = ['q0_q2']
  delta(q0_q2,  a) = ['q0_q1']
  delta(q0_q2,  b) = ['q0']
is_deterministic: True
```

The non-determinism in $\delta(q_0, a)$ is resolved by creating the composite state `q0_q1`. The original three NDFA states produce exactly three DFA states (no state explosion in this case), and the converted DFA correctly accepts any string ending with `ab`.

---

## Conclusions

This pair of laboratory works explored the close relationship between regular grammars and finite automata from both theoretical and practical perspectives.

The implementation confirmed that Variant 15's grammar is **Type 3 (Regular)** because all of its production rules follow the right-linear pattern $A \rightarrow aB$ or $A \rightarrow a$. The corresponding FA produced by `to_finite_automaton()` is immediately a DFA — no non-determinism arises from this particular grammar's structure.

The Chomsky classification algorithm works by testing the most restrictive type first and falling through. The key insight is that the tests are *inclusive upward*: a Type 3 grammar trivially satisfies the Type 2 constraints, a Type 2 grammar satisfies Type 1, and so on. Testing from the bottom prevents misclassification.

The Subset Construction algorithm is the central result of Lab 2. Its correctness rests on the observation that a DFA can simulate an NDFA by tracking *all possible states* the NDFA could be in simultaneously. The exponential worst-case ($2^{|Q|}$ states) does not occur here because most subsets are unreachable — the `q0/q1/q2` example produces only 3 DFA states from 3 NDFA states.

The formal verification step (testing generated strings against both the original FA and the converted DFA) provides empirical confidence that the conversion is semantically correct: both machines accept and reject exactly the same set of strings.

---

## References

[1] Hopcroft, J. E., Motwani, R., & Ullman, J. D. — *Introduction to Automata Theory, Languages, and Computation*, 3rd ed., Pearson, 2006.  
[2] Sipser, M. — *Introduction to the Theory of Computation*, 3rd ed., Cengage, 2012.  
[3] [Lexical Analysis — Wikipedia](https://en.wikipedia.org/wiki/Lexical_analysis)  
[4] [Powerset Construction — Wikipedia](https://en.wikipedia.org/wiki/Powerset_construction)
