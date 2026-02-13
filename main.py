import random

class Grammar:

    def __init__(self, V_n: set[str], V_t: set[str], P: dict[str, list[str]], S: str):
        self.V_n = V_n      #SET of nonterminal values
        self.V_t = V_t      #SET of terminal values
        self.P = P          #DICTIONARY of transformations
        self.S = S          #STRING of initial state

    def generate_string(self) -> str:
        language_string = self.S
        while not self.is_terminal(language_string):
            available_non_terminals = [char for char in language_string if char in self.V_n]
            if not available_non_terminals:
                break

            target = available_non_terminals[0]
            if target in self.P:
                replacement = random.choice(self.P[target])
                language_string = language_string.replace(target, replacement, 1)
        return language_string


    def is_terminal(self, state: str) -> bool:
        return all(char not in self.V_n for char in state)

    def to_finite_automaton(self):
        Q = self.V_n | {'X'}
        Sigma = self.V_t
        q0 = self.S
        delta = {}
        F = {'X'}

        for state, rules in self.P.items():
            for rule in rules:
                if len(rule) == 2 and rule[0] in Sigma and rule[1] in self.V_n:
                    terminal, next_state = rule[0], rule[1]
                    delta.setdefault((state, terminal), []).append(next_state)

                elif len(rule) == 1 and rule in Sigma:
                    terminal = rule
                    delta.setdefault((state, terminal), []).append('X')
        return FiniteAutomaton(Q, Sigma, delta, q0, F)
    
class FiniteAutomaton:
    def __init__(self, Q, Sigma, delta, q0, F):
        self.Q = Q
        self.Sigma = Sigma
        self.delta = delta
        self.q0 = q0
        self.F = F
    
    def string_belong_to_language(self, input_string: str) -> bool:
        current_states = {self.q0}

        for char in input_string:
            next_states = set()
            for state in current_states:
                if (state, char) in self.delta:
                    next_states.update(self.delta[(state,char)])
            current_states = next_states
            if not current_states:
                return False
        return any(state in self.F for state in current_states)

if __name__ == "__main__":
    v_n = {"S", "A", "B", "C"}
    v_t = {"a", "b", "c"}
    p = {
        "S": ["aA", "bB", "cC", "aB", "aC", "bA", "bC", "cA", "cB"],
        "A": ["aB", "c"],
        "B": ["bC", "a"],
        "C": ["cA", "b"]
    }
    s = "S"

    grammar = Grammar(v_n, v_t, p, s)

    print("Generating strings:")
    generated_examples = []
    for _ in range(5):
        word = grammar.generate_string()
        generated_examples.append(word)
        print(word)
    
    print()
    print("FA validation:")
    fa = grammar.to_finite_automaton()

    for word in generated_examples:
        is_valid = fa.string_belong_to_language(word)
        print(f"{word} -> {is_valid}")

    test_str = "abc"
    print("Test:")
    print(f"{word} -> {is_valid}")