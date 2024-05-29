import os

def dynamic_round(value: int|float, threshold: int=3) -> int|float:
	"""
	Rounds a number when there is repeating 9s or 0s in the decimal part.

	Parameters
	----------
	value (int|float): The number to round.
	threshold (int): The number of repeating 9s or 0s to consider for rounding.

	Returns
	-------
	int | float
		The rounded number.

	Examples
	--------
	>>> dynamic_round(3.14159, 3)
	3.14159
	>>> dynamic_round(0.0005163749999999999, 3)
	0.000516375
	>>> dynamic_round(2.2680000000000003e-05, 3)
	2.268e-05
	"""
	assert threshold >= 1, "The threshold must be greater than or equal to 1."

	str_value = str(value)
	if '.' in str_value:
		int_part, dec_part = str_value.split('.')
		dec_part, exponent_part = dec_part.split('e') if 'e' in dec_part else (dec_part, '')
		exponent_part = 'e' + exponent_part if exponent_part else ''

		if len(dec_part) > threshold:
			consecutive_0, first_consecutive_0_index = 0, None
			consecutive_9, first_consecutive_9_index = 0, None

			# Check for repeating 0s
			if '0' * threshold in dec_part:
				avoiding_initial_zeros = True
				for i, digit in enumerate(dec_part):
					if digit == '0':
						if avoiding_initial_zeros:
							continue
						consecutive_0 += 1
						if first_consecutive_0_index is None:
							first_consecutive_0_index = i

						if consecutive_0 == threshold:
							break
						
					else:

						avoiding_initial_zeros = False
						consecutive_0 = 0
						first_consecutive_0_index = None

			# Check for repeating 9s
			if '9' * threshold in dec_part:
				for i, digit in enumerate(dec_part):
					if digit == '9':
						consecutive_9 += 1
						if first_consecutive_9_index is None:
							first_consecutive_9_index = i

						if consecutive_9 == threshold:
							break
						
					else:
						consecutive_9 = 0
						first_consecutive_9_index = None

			bool_0 = (consecutive_0 == threshold) and (first_consecutive_0_index is not None)
			bool_9 = (consecutive_9 == threshold) and (first_consecutive_9_index is not None)

			# Return the rounded value
			if bool_0 and bool_9:
				# Return the values with less decimal places (meaning that found the pattern first)
				if first_consecutive_9_index < first_consecutive_0_index:
					rounded_decimal = round(float(f"{int_part}.{dec_part}"), first_consecutive_0_index + 1)
					completed_str_value = f"{rounded_decimal}{exponent_part}"
					return float(completed_str_value)
				else:
					rounded_decimal = round(float(f"{int_part}.{dec_part}"), first_consecutive_9_index + 1)
					completed_str_value = f"{rounded_decimal}{exponent_part}"
					return float(completed_str_value)
				
			elif bool_0:
				rounded_decimal = round(float(f"{int_part}.{dec_part}"), first_consecutive_0_index + 1)
				completed_str_value = f"{rounded_decimal}{exponent_part}"
				return float(completed_str_value)
			
			elif bool_9:
				rounded_decimal = round(float(f"{int_part}.{dec_part}"), first_consecutive_9_index + 1)
				completed_str_value = f"{rounded_decimal}{exponent_part}"
				return float(completed_str_value)
			
	return value


def split_input(file_path: str|None=None, file_text: str|None=None) -> tuple[str, list[str]]:
	"""
	Splits the grammar text and the words to parse from a file or a text.

	Parameters
	----------
	file_path (str, optional): The path to the file containing the grammar and the words to parse.
	file_text (str, optional): The text containing the grammar and the words to parse.

	Returns
	-------
	tuple[str, list[str]]
		The grammar text and the words to parse.
	"""
	assert (file_path is not None) or (file_text is not None), "Please provide a file path or a text to split the input."

	# Read the file or split the text
	if file_path is not None:	
		if not os.path.isfile(file_path):
			raise FileNotFoundError(f"File '{file_path}' not found. Please provide a valid file path to get the grammar and the words to parse.")
		
		lines = open(file_path, 'r', encoding="utf-8").readlines()
	
	elif file_text is not None:
		lines = file_text.split('\n')
	
	# Split the grammar and the words
	rules_text, words_text = '', ''
	rules_started, rules_ended = False, False

	for line in lines:
		line = line.strip()
		if not line or line.startswith('#'): # Skip empty lines and comments
			continue

		if (not rules_ended) and ((not rules_started) or ('->' in line)):
			rules_text += f"{line}\n"
			rules_started = True
		else:
			rules_ended = True
			words_text += f"{line}\n"

	list_words = words_text.strip().split()
	list_words = [word.strip() for word in list_words if word.strip()]

	return rules_text, list_words
