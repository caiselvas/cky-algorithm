from src.cfg import CFG
from src.cky import CKY
from src.functions import split_input

# Load the grammar from the file
rules_text, words = split_input('./tests/prob1.txt')
cfg = CFG(from_text=rules_text)

# Parse the words using the CKY algorithm
cky = CKY(cfg)

results = []
for word in words:
	result = cky.parse(word=word, round_probabilities=True)
	results.append(result)

# Print the results
print("CKY PARSING RESULTS:")
for result, word in zip(results, words):
	if cfg.is_probabilistic():
		parsed, prob, tree = result
		if parsed:
			print(f"'{word}' --> {parsed} [{prob}] | {tree}\n")
		else:
			print(f"'{word}' --> {parsed}\n")
	else:
		parsed, tree = result
		if parsed:
			print(f"'{word}' --> {parsed} | {tree}\n")
		else:
			print(f"'{word}' --> {parsed}\n")

