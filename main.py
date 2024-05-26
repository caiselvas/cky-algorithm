from src.cfg import CFG
from src.cky import CKY
from src.functions import split_input

# Read the input from the stdin
input_text = ''
while True:
	try:
		line = input()
		input_text += f"{line}\n"
	except EOFError:
		break

# Powershell command to set a file as stdin
# Get-Content .\input.txt | python .\main.py

rules_text, words = split_input(file_text=input_text)
cfg = CFG(from_text=rules_text)

# Parse the words using the CKY algorithm
cky = CKY(cfg)

results = []
for word in words:
	result = cky.parse(word=word, round_probabilities=True)
	results.append(result)

# Save the results to a file
save_path = f'./results/results_{'prob' if cfg.is_probabilistic() else 'det'}.txt'

save_file = open(save_path, 'w')

save_file.write(f"{cfg}\n")
save_file.write(f"{'*' * 80}\n\n")

# Write the results to the file
for result, word in zip(results, words):
	if cfg.is_probabilistic():
		parsed, prob, tree = result
		if parsed:
			save_file.write(f"{word} -> {parsed} [{prob}]\nTREE -> {tree}\n")
		else:
			save_file.write(f"{word} -> {parsed}\n")
	else:
		parsed, tree = result
		if parsed:
			save_file.write(f"{word} -> {parsed}\nTREE -> {tree}\n")
		else:
			save_file.write(f"{word} -> {parsed}\n")

	save_file.write('\n')
