import random

class Grammar:

    def __init__(self, V_n , V_t, P, S: str):
        self.V_n = V_n      #SET of nonterminal values
        self.V_t = V_t      #SET of terminal values
        self.P = P          #DICTIONARY of transformations
        self.S = S          #STRING of initial state

    def generate_string(self) -> str:
        language_string = str(self.S)     #copy the inital state to apply further random transformations
        P_source = list(self.P.keys())
        randindex = 0
        toreplace = ""
        while not self.isterminal(language_string):
            randindex = random.randint(0, len(P_source) - 1)                        #index of the randomly chosed key of the P dictionary
            toreplace = self.P.get(P_source[randindex])                         #toreplace - the value that will replace the given substring
            #print(P_source[randindex], toreplace)
            language_string = language_string.replace(P_source[randindex], toreplace, 1)          #replaces the old substring with the procedure one, only the first occurance
            #print(language_string) 
        return language_string


    def isterminal(self, state: str) -> bool:
        for nonterminal in self.V_n:
            if state.count(nonterminal) > 0:
                return False
        return True


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
