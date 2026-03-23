# Regular Expressions & String Generation
**Course:** Formal Languages & Finite Automata  
**Author:** Cretu Dumitru  
**Collaborators:** Vasile Drumea, Irina Cojuhari  

---

## 1. Introduction
Regular Expressions (Regex) are sequences of characters that define a search pattern. In the context of Formal Languages, they represent a declarative way to describe **Regular Languages**. They are fundamental to computer science, particularly in:
* **Lexical Analysis:** Identifying tokens during the first phase of compilation.
* **Data Validation:** Ensuring input data conforms to specific patterns.
* **Text Processing:** Efficiently searching and manipulating strings.

## 2. Objectives
The primary objective of this project is to implement a system that interprets regular expressions **dynamically**. Unlike a hardcoded string generator, this implementation treats a set of regex rules as input and produces valid word combinations as output.

**Requirements Checklist:**
1.  **Dynamic Interpretation:** The engine should process logic (alternation, repetition) rather than returning static strings.
2.  **Quantifier Limits:** For operators with undefined lengths (like `*` and `+`), a maximum limit of **5 repetitions** is enforced to keep outputs manageable.
3.  **Bonus Point:** Implementation of a trace function to display the sequence of processing for each generated string.

## 3. Variant 4 Analysis
This project focuses on the three regular expressions assigned to **Variant 4**. The following table breaks down the structural logic for each:

| No. | Regular Expression | Logic Components |
| :--- | :--- | :--- |
| **1** | $(S\|T)(U\|V)w^*y^+24$ | Alternation $(S/T, U/V)$, Kleene Star ($w$), Kleene Plus ($y$), Literal (24). |
| **2** | $L(M\|N)O^3P^*Q(2\|3)$ | Literal ($L$), Alternation $(M/N)$, Fixed Repetition ($O^3$), Kleene Star ($P^*$), Literal ($Q$), Alternation ($2/3$). |
| **3** | $R^*S(T\|U\|V)W(X\|Y\|Z)^2$ | Kleene Star ($R^*$), Literal ($S$), Triple Alternation ($T/U/V$), Literal ($W$), Set Choice with fixed repetition ($2$). |

## 4. Implementation Details
The core logic is implemented in Python using a **Token-Based Generation** approach. Instead of using a standard regex library to match text, this program interprets a schema to *build* text.

### The Generation Engine
The generator iterates through a list of instructions:
* **Choice Nodes:** Randomly selects one element from a provided list.
* **Repetition Nodes:** Handles `*` (0–5), `+` (1–5), and fixed integers (e.g., $O^3$).
* **Sequence Tracing:** A separate logger records each "decision" the engine makes (e.g., "Selected 'S' from ['S', 'T']").

## 5. Sequence of Processing (Bonus)
Each generation cycle produces a trace. This is crucial for verifying that the "dynamic" requirement is met. 

**Example Trace (Regex 2):**
1.  **Literal** 'L' added.
2.  **Choice** from `['M', 'N']`: Selected 'M'.
3.  **Fixed Repetition**: 'O' repeated 3 times -> 'OOO'.
4.  **Star Repetition**: 'P' repeated 2 times -> 'PP'.
5.  **Literal** 'Q' added.
6.  **Choice** from `['2', '3']`: Selected '3'.
7.  **Result:** `LMOOOPPQ3`

## 6. Usage
1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/your-username/your-repo-name.git](https://github.com/your-username/your-repo-name.git)
    ```
2.  **Run the Script:**
    ```bash
    python src/reg.py
    ```

## 7. Challenges & Conclusions
The most significant difficulty was abstracting the regex logic. Moving from a hardcoded `if-else` structure to a truly dynamic system required representing regex components as data objects. This project successfully demonstrates how a generator can act as the inverse of a lexer, producing valid strings from the same formal rules that a scanner would use to recognize them.

---
**Deadline:** March 26, 2026 
