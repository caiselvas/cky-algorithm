import nltk
from nltk import CFG
from nltk.parse.generate import generate

def compare_grammars(grammar1_str, grammar2_str, max_len=1000):
    """
    Compares two grammars to check if they are equivalent by comparing their productions
    and generating sentences up to a certain length.

    Parameters
    ----------
    grammar1_str (str): The string representation of the first grammar.
    grammar2_str (str): The string representation of the second grammar.
    max_len (int): The maximum length of sentences to generate for comparison.

    Returns
    -------
    bool
        True if the grammars are equivalent, False otherwise.
    """
    # Parse the grammars from the provided strings
    grammar1 = CFG.fromstring(grammar1_str)
    grammar2 = CFG.fromstring(grammar2_str)
    
    # Generate sentences up to max_len for both grammars
    gen_sentences_grammar1 = set(tuple(sentence) for sentence in generate(grammar1, depth=max_len))
    gen_sentences_grammar2 = set(tuple(sentence) for sentence in generate(grammar2, depth=max_len))
    
    # Compare the generated sentences
    equivalent = gen_sentences_grammar1 == gen_sentences_grammar2
    print(f"The grammars generate the same language (within the tested length): {equivalent}")
    return equivalent

# Grammars to compare
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

equivalent = compare_grammars(grammar1_str, grammar2_str)