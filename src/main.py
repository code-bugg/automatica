"""
Lab 5 — Chomsky Normal Form
Variant 15: G=({S,A,B,C,D},{a,b},P,S)
"""

from copy import deepcopy


class Grammar:
    def __init__(self, variables, terminals, productions, start):
        self.variables = set(variables)
        self.terminals = set(terminals)
        self.productions = {k: [list(r) for r in v] for k, v in productions.items()}
        self.start = start
        self._counter = 0

    def _fresh(self, prefix="X"):
        while True:
            name = f"{prefix}{self._counter}"
            self._counter += 1
            if name not in self.variables:
                return name

    def clone(self):
        g = Grammar(deepcopy(self.variables), deepcopy(self.terminals),
                    deepcopy(self.productions), self.start)
        g._counter = self._counter
        return g

    # Step 1
    def eliminate_epsilon(self):
        g = self.clone()
        nullable = set()
        changed = True
        while changed:
            changed = False
            for lhs, rhss in g.productions.items():
                if lhs not in nullable:
                    for rhs in rhss:
                        if rhs in ([""], []) or all(s in nullable for s in rhs):
                            nullable.add(lhs); changed = True; break

        new_prods = {}
        for lhs, rhss in g.productions.items():
            new_prods[lhs] = []
            for rhs in rhss:
                if rhs in ([""], []):
                    continue
                np = [i for i, s in enumerate(rhs) if s in nullable]
                for mask in range(1 << len(np)):
                    omit = {np[j] for j in range(len(np)) if mask & (1 << j)}
                    nr = [s for i, s in enumerate(rhs) if i not in omit]
                    if nr and nr not in new_prods[lhs]:
                        new_prods[lhs].append(nr)
        g.productions = new_prods
        return g

    # Step 2
    def eliminate_unit_rules(self):
        g = self.clone()
        pairs = {(v, v) for v in g.variables}
        changed = True
        while changed:
            changed = False
            for lhs, rhss in g.productions.items():
                for rhs in rhss:
                    if len(rhs) == 1 and rhs[0] in g.variables:
                        for (a, b) in list(pairs):
                            if b == lhs and (a, rhs[0]) not in pairs:
                                pairs.add((a, rhs[0])); changed = True

        new_prods = {v: [] for v in g.variables}
        for (a, b) in pairs:
            for rhs in g.productions.get(b, []):
                if not (len(rhs) == 1 and rhs[0] in g.variables):
                    if rhs not in new_prods[a]:
                        new_prods[a].append(rhs)
        g.productions = new_prods
        return g

    # Step 3
    def eliminate_inaccessible(self):
        g = self.clone()
        reachable = {g.start}
        changed = True
        while changed:
            changed = False
            for lhs, rhss in g.productions.items():
                if lhs not in reachable: continue
                for rhs in rhss:
                    for s in rhs:
                        if s in g.variables and s not in reachable:
                            reachable.add(s); changed = True
        g.variables = reachable
        g.productions = {k: v for k, v in g.productions.items() if k in reachable}
        return g

    # Step 4
    def eliminate_non_productive(self):
        g = self.clone()
        productive = set()
        changed = True
        while changed:
            changed = False
            for lhs, rhss in g.productions.items():
                if lhs not in productive:
                    for rhs in rhss:
                        if all(s in g.terminals or s in productive for s in rhs):
                            productive.add(lhs); changed = True; break
        g.variables &= productive
        g.productions = {
            lhs: [r for r in rhss if all(s in g.terminals or s in g.variables for s in r)]
            for lhs, rhss in g.productions.items() if lhs in g.variables
        }
        return g

    # Step 5
    def to_cnf(self):
        g = self.clone()
        term_map = {}
        for t in g.terminals:
            v = g._fresh(t.upper() + "_")
            term_map[t] = v
            g.variables.add(v)
            g.productions[v] = [[t]]

        new_prods = {v: [] for v in g.variables}
        for lhs, rhss in g.productions.items():
            for rhs in rhss:
                if len(rhs) == 1:
                    new_prods[lhs].append(rhs)
                else:
                    nr = [term_map[s] if s in g.terminals else s for s in rhs]
                    while len(nr) > 2:
                        cv = g._fresh("Z")
                        g.variables.add(cv)
                        new_prods[cv] = [nr[-2:]]
                        nr = nr[:-2] + [cv]
                    if nr not in new_prods[lhs]:
                        new_prods[lhs].append(nr)
        for v in g.variables:
            if v not in new_prods:
                new_prods[v] = []
        g.productions = new_prods
        return g

    def normalize(self):
        steps = [
            ("1. Eliminate ε-productions",        Grammar.eliminate_epsilon),
            ("2. Eliminate unit rules",            Grammar.eliminate_unit_rules),
            ("3. Eliminate inaccessible symbols",  Grammar.eliminate_inaccessible),
            ("4. Eliminate non-productive symbols",Grammar.eliminate_non_productive),
            ("5. Convert to CNF",                  Grammar.to_cnf),
        ]
        g = self
        for name, fn in steps:
            g = fn(g)
            print(f"\n{'─'*55}")
            print(f" {name}")
            print('─'*55)
            print(g)
        return g

    def is_cnf(self):
        for lhs, rhss in self.productions.items():
            for rhs in rhss:
                if len(rhs) == 1 and rhs[0] in self.terminals: continue
                if len(rhs) == 2 and all(s in self.variables for s in rhs): continue
                return False
        return True

    def __str__(self):
        lines = [f"  Vars : {sorted(self.variables)}",
                 f"  Terms: {sorted(self.terminals)}",
                 f"  Start: {self.start}", "  Rules:"]
        for lhs in sorted(self.productions):
            if self.productions[lhs]:
                rhs_str = " | ".join(" ".join(r) if r else "ε" for r in self.productions[lhs])
                lines.append(f"    {lhs} → {rhs_str}")
        return "\n".join(lines)


# ── Variant 15 ────────────────────────────────────────────────────────────────
g = Grammar(
    variables={"S", "A", "B", "C", "D"},
    terminals={"a", "b"},
    productions={
        "S": [["A","C"], ["b","A"], ["B"], ["a","A"]],
        "A": [[""],      ["a","S"], ["A","B","a","b"]],
        "B": [["a"],     ["b","S"]],
        "C": [["a","b","C"]],
        "D": [["A","B"]],
    },
    start="S",
)

print("═"*55)
print(" ORIGINAL GRAMMAR — Variant 15")
print("═"*55)
print(g)

cnf = g.normalize()

print(f"\n{'═'*55}")
print(" FINAL CNF GRAMMAR")
print("═"*55)
print(cnf)
print(f"\n  is_cnf() → {cnf.is_cnf()}")