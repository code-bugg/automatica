# Project Title: Laboratory Work 1 & 2 - Formal Languages & Finite Automata
### Course: Formal Languages & Finite Automata
### Author: Cretu Dumitru
### Kudos to: Vasile Drumea with Irina Cojuhari
---

## Overview
A formal language serves as a mechanism to convey information between a sender and a receiver. This project implements the fundamental components of a language:
* **Alphabet**: A set of valid characters (terminals).
* **Vocabulary**: Valid words formed by the alphabet.
* **Grammar**: A set of rules and constraints defining the language.

Across two laboratory works, the project grows from basic grammar and automaton construction to determinism analysis, Chomsky classification, and NDFA-to-DFA conversion.

---

## Lab 1 — Intro to Formal Languages

### Objectives
1. **Grammar Implementation**: Representation of a grammar as a programming object.
2. **String Generation**: Generating valid strings from the defined grammar.
3. **Grammar to Finite Automaton Conversion**: Mapping a regular grammar to a Finite Automaton (FA).
4. **String Validation**: Checking if an input string belongs to the language using the FA.

### Implementation Details

#### `Grammar` Class
* `__init__`: Initializes the non-terminals ($V_n$), terminals ($V_t$), production rules ($P$), and the start symbol ($S$).
* `generate_string`: Applies random production rules from $P$ to transform the start symbol into a terminal string.
* `to_finite_automaton`: Converts the grammar object into a `FiniteAutomaton` object based on regular grammar rules ($A \rightarrow aB$ or $A \rightarrow a$).

#### `FiniteAutomaton` Class
* `__init__`: Sets up the states ($Q$), alphabet ($\Sigma$), transition function ($\delta$), start state ($q_0$), and final states ($F$).
* `string_belong_to_language`: Simulates the automaton to check if an input string is accepted.

---

## Lab 2 — Determinism in Finite Automata, NDFA to DFA, Chomsky Hierarchy

### Objectives
1. **Chomsky Classification**: Classify a grammar according to the Chomsky hierarchy (Type 0–3).
2. **FA to Regular Grammar**: Convert a finite automaton back into a regular grammar.
3. **Determinism Check**: Determine whether a given FA is deterministic (DFA) or non-deterministic (NDFA).
4. **NDFA to DFA Conversion**: Implement the subset construction algorithm to convert an NDFA into an equivalent DFA.

### Implementation Details

#### `Grammar.classify()`
Checks productions from strictest to most permissive and returns the most restrictive type that applies:
* **Type 3 (Regular)**: All rules are right-linear ($A \rightarrow aB$ or $A \rightarrow a$) or all left-linear ($A \rightarrow Ba$ or $A \rightarrow a$).
* **Type 2 (Context-Free)**: Every LHS is a single non-terminal.
* **Type 1 (Context-Sensitive)**: $|lhs| \leq |rhs|$ for all productions (with the standard exception for $S \rightarrow \varepsilon$).
* **Type 0 (Unrestricted)**: No additional constraints.

#### `FiniteAutomaton.to_regular_grammar()`
Constructs a right-linear grammar from the FA by iterating over every transition $\delta(A, a) = B$ and emitting:
* $A \rightarrow aB$ for non-accepting target states.
* $A \rightarrow a$ when the target state is a final state.

#### `FiniteAutomaton.is_deterministic()`
An FA is a DFA if and only if every $(state, symbol)$ pair maps to **at most one** next state. The method scans all transition entries and returns `False` as soon as any entry contains more than one target.

#### `FiniteAutomaton.to_dfa()`
Implements the classic **subset construction** algorithm:
1. The start state of the DFA is the frozenset `{q0}`.
2. For each unvisited DFA state (a set of NDFA states) and each symbol, compute the union of reachable NDFA states.
3. A DFA state is accepting if it contains at least one NDFA accepting state.
4. State sets are renamed to readable strings by joining sorted member names with `_` (e.g. `A_B_C`).

---

## Project Structure
* `main.py` / `lab2.py`: Contains the `Grammar` and `FiniteAutomaton` classes along with demonstration logic in the `__main__` block.
* `task.md`: Original requirements for the laboratory work.
* `README.md`: This file.

---

## Results

The variant grammar used throughout:

| Non-terminals | Terminals | Start |
|---|---|---|
| S, A, B, C | a, b, c | S |

Productions: `S → aA | bB | cC | aB | aC | bA | bC | cA | cB`, `A → aB | c`, `B → bC | a`, `C → cA | b`

* **Chomsky type**: Type 3 (Regular) — all rules are right-linear.
* **Determinism**: The FA derived from this grammar is an **NDFA** (e.g. from state `S`, all three symbols lead to multiple possible next states).
* **After conversion**: The subset construction produces a valid DFA confirmed by `is_deterministic() = True`, and a sanity check verifies both automata accept exactly the same strings.

---

## Evaluation
This project is stored in a public GitHub repository as required.

---
*Lab 1 Deadline: 12-th February, 2026*
*Lab 2 Deadline: 26-th February, 2026*