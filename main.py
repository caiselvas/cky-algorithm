from src.cfg import CFG
from src.cky import CKY
from src.functions import split_input
import os

def main(input_text: str, file_name: str):
	rules_text, words = split_input(file_text=input_text)
	cfg = CFG(from_text=rules_text)

	# Parse the words using the CKY algorithm
	cky = CKY(cfg)

	results = []
	for word in words:
		result = cky.parse(word=word, round_probabilities=True)
		results.append(result)

	# Save the results to a file
	save_path = os.path.join('./results', f"results_{file_name}")

	save_file = open(save_path, 'w', encoding='utf-8')

	save_file.write(f"{cfg}\n")
	save_file.write(f"{'#' * 50}\n\n")

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

	save_file.close()

	print(f"Results saved to '{save_path}'.")

if __name__ == '__main__':
	all_files = False
	first_n_files = None
	# Read the input from the stdin
	while True:
		try:
			file_name = input("File: ")
			if not file_name:
				raise ValueError("Please provide a valid file name.")
			
			elif file_name.lower() == 'all':
				all_files = True
			
			elif not os.path.isfile(os.path.join('./tests', file_name)):
				raise FileNotFoundError(f"File '{file_name}' not found. Please provide a valid file name in the folder './tests'.")
			
			break
		except ValueError as e:
			print(e)

	# Get the list of files to process
	files_list = os.listdir('./tests') if all_files else [file_name]

	for file_name in files_list:
		with open(os.path.join('./tests', file_name), 'r', encoding='utf-8') as file:
			input_text = file.read()
			main(input_text=input_text, file_name=file_name)
			print(f"Processed file '{file_name}' successfully.")

	print("All files processed successfully!")
