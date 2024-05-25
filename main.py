from src.cfg import CFG
from src.cky import CKY
from src.functions import dynamic_round

# Load the grammar from the file
grammar = CFG(probabilistic=True, from_file="./tests/prob1.txt")

print(grammar)

