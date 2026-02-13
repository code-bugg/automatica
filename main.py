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


    def isterminal(self, state: str) -> bool:
        return all(char not in self.V_n for char in state)

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
                current_states

                if not current_states:
                    return False
            return any(state in self.F for state in current_states)

if __name__ == "__main__":
    some_P = {
            "AB": "aB",
            "A": "aa",
            "Ba": "bbA",
            "Bb": "bBa"
    }
    some_V_n = set(("A", "B"))
    some_V_t = set(("a", "b"))
    some_S = "ABBA"
    
    some_grammar = Grammar(some_V_n, some_V_t, some_P, some_S)

    for i in range(5):
        print(some_grammar.generate_string())    
