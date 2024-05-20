import nltk
from nltk import CFG

def compare_grammars(grammar1_str, grammar2_str):
    """
    Compares two grammars to check if they are equivalent.

    Parameters
    ----------
    grammar1_str (str): The string representation of the first grammar.
    grammar2_str (str): The string representation of the second grammar.

    Returns
    -------
    bool
        True if the grammars are equivalent, False otherwise.
    """
    # Parse the grammars from the provided strings
    grammar1 = CFG.fromstring(grammar1_str)
    grammar2 = CFG.fromstring(grammar2_str)
    
    # Compare the sets of productions
    return set(grammar1.productions()) == set(grammar2.productions())

# Grammar examples
grammar1_str = """
    S -> NP VP
    NP -> 'John' | 'Mary'
    VP -> V NP
    V -> 'loves' | 'hates'
"""

grammar2_str = """
    S -> NP VP
    VP -> V NP
    NP -> 'John' | 'Mary'
    V -> 'loves' | 'hates'
"""

# Compare the grammars
equivalent = compare_grammars(grammar1_str, grammar2_str)
print(f"Equivalent grammars: {equivalent}")
