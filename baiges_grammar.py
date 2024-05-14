class Grammar:
    def __init__(self):
        self.rules = {}
        self.ternimal_rules = {}
        self.non_terminal_rules = {}

    def set_rules(self, rules):
        self.rules = rules

    def check_if_CNF(self):
        for lhs, rhs in self.rules.items():
            if not lhs.isupper():
                return False
            for rule in rhs:
                if len(rule) == 2:
                    if rule[0].isupper() and rule[1].isupper():
                        continue
                    else:
                        return False
                elif len(rule) == 1:
                    if rule[0].islower():
                        continue
                    else:
                        return False
                else:
                    return False
        return True

    def __run__(self, rule):
        return self.rules[rule]

    def __str__(self):
        return f"Grammar({self.rules})"


# NOT CNF Grammar
grammar1 = Grammar()
grammar1.set_rules({
    "S": ["aA", "B"],
    "A": ["a"],
    "B": ["b", "C"],
    "C": ["cD"],
    "D": ["d"]
})

print(f"Grammar 1 is in CNF: {grammar1.check_if_CNF()}")


# CNF Grammar
grammar2 = Grammar()
grammar2.set_rules({
    "S": ["AB", "BC"],
    "A": ["a"],
    "B": ["b"],
    "C": ["CD", "c"],
    "D": ["d"]
})

print(f"Grammar 2 is in CNF: {grammar2.check_if_CNF()}")

