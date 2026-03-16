import random
from collections import defaultdict

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
    
    def classify(self) -> str:
        if self._is_type3():
            return "Type 3 (regular)"
        if self._is_type2():
            return "Type 2 (context-free)"
        if self._is_type1():
            return "Type 1 (context-sensitive)"
        return "Type 0 (unrestricted)"

    def _is_type3(self) -> bool:
        right_linear = True
        left_linear = True
        for lhs, productions in self.P.items():
            if lhs not in self.V_n or len(lhs) != 1:
                right_linear = left_linear = False
                break
            for rhs in productions:
                is_rl = (
                        (len(rhs) == 1 and rhs in self.V_t) or
                        (len(rhs) == 2 and rhs[0] in self.V_t and rhs[1] in self.V_n)
                )
                is_ll = (
                        (len(rhs) == 1 and rhs in self.V_t) or
                        (len(rhs) == 2 and rhs[0] in self.V_n and rhs[1] in self.V_t)
                )
                if not is_rl:
                    right_linear = False
                if not is_ll:
                    left_linear = False
        return right_linear or left_linear

    def _is_type2(self) -> bool:
        for lhs in self.P:
            if len(lhs) != 1 or lhs not in self.V_n:
                return False
        return True

    def _is_type1(self) -> bool:
        for lhs, productions in self.P.items():
            for rhs in productions:
                if rhs == '' or rhs == 'epsilon':
                    if lhs == self.S and all(
                            lhs not in r for rules in self.P.values() for r in rules
                    ):
                        continue
                    return False
                if len(lhs) > len(rhs):
                    return False
        return True

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
    
    def to_regular_grammar(self) -> Grammar:
        V_n = set(self.Q)
        V_t = set(self.Sigma)
        P = defaultdict(list)

        for (state, symbol), targets in self.delta.items():
            for t in targets:
                if t in self.F:
                    P[state].append(symbol)
                P[state].append(symbol + t)

        P = {k: list(dict.fromkeys(v)) for k, v in P.items()}
        return Grammar(V_n, V_t, dict(P), self.q0)

    def is_deterministic(self) -> bool:
        for targets in self.delta.values():
            if len(targets) > 1:
                return False
        return True

    def to_dfa(self) -> 'FiniteAutomaton':
        start = frozenset({self.q0})
        dfa_delta = {}
        unvisited = [start]
        visited = set()
        visited.add(start)

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

        dfa_Q = visited
        dfa_F = {s for s in dfa_Q if s & self.F}

        def name(fs):
            return '_'.join(sorted(fs)) if fs else 'DEAD'
        
        renamed_delta = {}
        for (src, sym), [tgt] in dfa_delta.items():
            renamed_delta[(name(src), sym)] = [name(tgt)]

        return FiniteAutomaton(
            Q={name(s) for s in dfa_Q},
            Sigma=self.Sigma,
            delta=renamed_delta,
            q0=name(start),
            F={name(s) for s in dfa_F}
        )

    def __str__(self):
        lines = [
            f"States (Q)            : {sorted(self.Q)}",
            f"Alphabet (Sigma)      : {sorted(self.Sigma)}",
            f"Start state (q0)      : {self.q0}",
            f"Final states (F)      : {sorted(self.F)}",
        ]
        for (s, a), tgts in sorted(self.delta.items()):
            lines.append(f"     delta({s}, {a}) = {tgts}")
        return "\n".join(lines)

if __name__ == "__main__":
    v_n = {"S", "A", "B"}
    v_t = {"a", "b", "c"}
    p = {
        "S": ["aS", "bS", "cA"],
        "A": ["aB"],
        "B": ["aB", "bB", "c"]
    }
    s = "S"

    grammar = Grammar(v_n, v_t, p, s)
    #print the grammar class 
    print("Grammar type verification: ", grammar.classify())
    
    print("Generating strings:")
    generated_examples = []
    for _ in range(5):
        word = grammar.generate_string()
        generated_examples.append(word)
        print(word)
    
    print()

    #working with the casting of grammar to automaton
    print("FA validation:")
    fa = grammar.to_finite_automaton()
    #retrieve the regular grammar from the finite automaton
    rg = fa.to_regular_grammar()
    print("     Non-terminals:  ", rg.V_n)
    print("     Terminals: ", rg.V_t)
    print("     Start symbol: ", rg.S)
    print("     Productions: ")
    for lhs, prods in sorted(rg.P.items()):
        print(f"        {lhs} -> {' | '.join(prods)}")
    print()

    #checking determinism of the finite automaton
    print("Determinism check")
    det = fa.is_deterministic()
    print(f"    FA is {'DETERMINISTIC (DFA)' if det else 'NON-DETERMINISTIC (NDFA)'}")
    print()

    #converting NDFA to DFA
    if not det:
        dfa = fa.to_dfa()
        print(dfa)
        print(f"    DFA is deterministic: {dfa.is_deterministic()}")
    else:
        print("     FA is already DFA - no conversion needed")
    print()

    #final verification
    print("Formal verification")
    dfa = fa.to_dfa()
    for _ in range(6):
        word = grammar.generate_string()
        ndfa_ok = fa.string_belong_to_language(word)
        dfa_ok = dfa.string_belong_to_language(word)
        match = "matched" if ndfa_ok == dfa_ok else "mismatched"
        print(f"    '{word}' NDFA = {ndfa_ok} DFA = {dfa_ok} {match}")
    print()

    #extra testing
    print("Additional testing")
    ndfa2 = FiniteAutomaton(
        Q={'q0', 'q1', 'q2'},
        Sigma={'a', 'b'},
        delta={
            ('q0', 'a'): ['q0', 'q1'],
            ('q0', 'b'): ['q0'],
            ('q1', 'b'): ['q2'],
        },
        q0='q0',
        F={'q2'}
    )
    print(ndfa2)
    print(ndfa2.is_deterministic())
    dfa2 = ndfa2.to_dfa()
    print(dfa2)
    print(dfa2.is_deterministic)
