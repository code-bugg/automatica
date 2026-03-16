# Laboratory Work 1 & 2: Formal Languages & Finite Automata

### Course: Formal Languages & Finite Automata
### Author: Cretu Dumitru
### Variant: 15
### Kudos to: Vasile Drumea with Irina Cojuhari

---

## 1. Overview
This project implements the foundational concepts of formal language theory. A formal language is defined by its alphabet, vocabulary, and grammar. Over the course of two laboratory works, this project has evolved from a basic string generator into a system capable of classifying grammars, analyzing the determinism of finite automata, and converting Non-deterministic Finite Automata (NDFA) into Deterministic Finite Automata (DFA).

All logic is implemented in a unified `main.py` file.

---

## 2. Objectives

### Laboratory Work 1
* **Grammar Implementation**: Representing $G = (V_n, V_t, P, S)$ as a programming object.
* **String Generation**: Deriving terminal strings from the start symbol $S$.
* **FA Conversion**: Mapping a regular grammar to its equivalent Finite Automaton.

### Laboratory Work 2
* **Chomsky Classification**: Identifying if a grammar is Type 0, 1, 2, or 3.
* **Determinism Analysis**: Determining if an FA is a DFA or NDFA.
* **NDFA to DFA Conversion**: Implementing the Subset Construction algorithm.
* **FA to Grammar Conversion**: Converting an automaton back into a Right-Linear grammar.

---

## 3. Implementation Details

### Variant 15 Grammar
The system is initialized with the following production rules ($P$):
* $S \rightarrow aS$ | $bS$ | $cA$
* $A \rightarrow aB$
* $B \rightarrow aB$ | $bB$ | $c$

### The `Grammar` Class
* **`generate_string()`**: Recursively replaces non-terminals in a string until the `isterminal()` condition is met.
* **`classify()`**: Analyzes production rules to determine the Chomsky type. For Variant 15, it detects **Type 3 (Regular)** because all rules are Right-Linear ($A \rightarrow aB$ or $A \rightarrow a$).
* **`to_finite_automaton()`**: Maps rules to states. For example, $A \rightarrow aB$ becomes a transition $\delta(A, a) = B$, and $B \rightarrow c$ transitions to a final state `X`.

### The `FiniteAutomaton` Class
* **`is_deterministic()`**: Checks if any state has more than one transition for a single input symbol. Variant 15 is identified as a **DFA**.
* **`to_dfa()`**: Implements the **Subset Construction Algorithm**. It creates sets of states (frozensets) to represent new DFA states. Even for an existing DFA, it correctly re-maps the states to ensure a deterministic structure.
* **`string_belong_to_language()`**: Processes an input string across the state transitions to verify if the final state reached is in the set of accepting states $F$.

---

## 4. Results

### Grammar Analysis
* **Type**: Type 3 (Regular)
* **Determinism**: The FA generated from Variant 15 is **Deterministic**.

### Subset Construction (NDFA to DFA)
The project demonstrates the conversion logic using an extra test case (`ndfa2`):
1.  Original NDFA states: `{q0, q1, q2}`.
2.  Transitions: `(q0, a)` leads to both `q0` and `q1`.
3.  Converted DFA: A new state `q0_q1` is created to handle the non-determinism, successfully making the machine deterministic.

### Example Derivations
| Input String | Path Taken | Result |
| :--- | :--- | :--- |
| `aacabac` | $S \rightarrow S \rightarrow S \rightarrow A \rightarrow B \rightarrow B \rightarrow X$ | **Accepted** |
| `caac` | $S \rightarrow A \rightarrow B \rightarrow B \rightarrow X$ | **Accepted** |
| `abc` | $S \rightarrow (\text{Invalid})$ | **Rejected** |

---

## 5. Conclusions
This laboratory work successfully demonstrated the deep connection between regular grammars and finite automata. By implementing the Chomsky classification and the subset construction algorithm, the project provides a robust tool for analyzing and transforming formal languages. The implementation confirms that Variant 15 is a Regular Grammar that produces a Deterministic Finite Automaton.

---

## 6. Evaluation
This project is stored in a public GitHub repository as required.

* **Lab 1 Deadline**: 12-th February, 2026
* **Lab 2 Deadline**: 26-th February, 2026
