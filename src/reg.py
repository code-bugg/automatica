import random

class RegexGenerator:
    def __init__(self, limit=5):
        self.limit = limit
        self.processing_steps = []

    def generate(self, pattern_schema):
        """
        pattern_schema: A list of tuples/objects representing the regex logic.
        Example: [('choice', ['S', 'T']), ('literal', 'w', '*')]
        """
        self.processing_steps = []
        result = ""
        
        for part in pattern_schema:
            type = part[0]
            
            if type == 'literal':
                char = part[1]
                quantifier = part[2] if len(part) > 2 else '1'
                
                count = 1
                if quantifier == '*':
                    count = random.randint(0, self.limit)
                elif quantifier == '+':
                    count = random.randint(1, self.limit)
                elif isinstance(quantifier, int):
                    count = quantifier
                
                fragment = char * count
                self.processing_steps.append(f"Literal '{char}' repeated {count} times -> {fragment}")
                result += fragment

            elif type == 'choice':
                options = part[1]
                repeat = part[2] if len(part) > 2 else 1
                
                choice_fragments = []
                for _ in range(repeat):
                    chosen = random.choice(options)
                    choice_fragments.append(chosen)
                
                fragment = "".join(choice_fragments)
                self.processing_steps.append(f"Choice from {options} selected {repeat} times -> {fragment}")
                result += fragment
                
        return result

# Define Variant 4 Schemas
v4_regex1 = [
    ('choice', ['S', 'T']),
    ('choice', ['U', 'V']),
    ('literal', 'w', '*'),
    ('literal', 'y', '+'),
    ('literal', '24')
]

v4_regex2 = [
    ('literal', 'L'),
    ('choice', ['M', 'N']),
    ('literal', 'O', 3),
    ('literal', 'P', '*'),
    ('literal', 'Q'),
    ('choice', ['2', '3'])
]

v4_regex3 = [
    ('literal', 'R', '*'),
    ('literal', 'S'),
    ('choice', ['T', 'U', 'V']),
    ('literal', 'W'),
    ('choice', ['X', 'Y', 'Z'], 2)
]

# Execution
gen = RegexGenerator()
print(f"Result 1: {gen.generate(v4_regex1)}")
for step in gen.processing_steps: print(f"  > {step}")

print(f"\nResult 2: {gen.generate(v4_regex2)}")
for step in gen.processing_steps: print(f"  > {step}")

print(f"\nResult 3: {gen.generate(v4_regex3)}")
for step in gen.processing_steps: print(f"  > {step}")