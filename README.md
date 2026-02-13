# Project Title: Laboratory Work 1 - Intro to Formal Languages

### Course: Formal Languages & Finite Automata
### Author: Cretu Dumitru
### Kudos to: Vasile Drumea with Irina Cojuhari

---

## Overview
A formal language serves as a mechanism to convey information between a sender and a receiver. This project implements the fundamental components of a language:
* **Alphabet**: A set of valid characters (terminals).
* **Vocabulary**: Valid words formed by the alphabet.
* **Grammar**: A set of rules and constraints defining the language.

## Objectives
This project demonstrates understanding of the following concepts:
1.  **Grammar Implementation**: Representation of a grammar as a programming object.
2.  **String Generation**: Generating valid strings from the defined grammar.
3.  **Grammar to Finite Automaton Conversion**: Mapping a regular grammar to a Finite Automaton (FA).
4.  **String Validation**: Checking if an input string belongs to the language using the FA.



## Project Structure
* `main.py`: Contains the `Grammar` and `FiniteAutomaton` classes, along with demonstration logic in the `__main__` block.
* `task.md`: Original requirements for the laboratory work.

## Implementation Details
### `Grammar` Class
* `__init__`: Initializes the non-terminals ($V_n$), terminals ($V_t$), production rules ($P$), and the start symbol ($S$).
* `generate_string`: Applies random production rules from $P$ to transform the start symbol into a terminal string.
* `to_finite_automaton`: Converts the grammar object into a `FiniteAutomaton` object based on regular grammar rules ($A \rightarrow aB$ or $A \rightarrow a$).

### `FiniteAutomaton` Class
* `__init__`: Sets up the states ($Q$), alphabet ($\Sigma$), transition function ($\delta$), start state ($q_0$), and final states ($F$).
* `string_belong_to_language`: Simulates the automaton to check if an input string is accepted.

## Evaluation
This project is stored in a public GitHub repository as required.

---
*Deadline: 12-th February, 2026*