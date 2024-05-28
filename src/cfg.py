import warnings
import os
from itertools import combinations
from collections import deque, defaultdict
from src.functions import dynamic_round
from typing import Any

class CFG:
	"""
	A class to represent a Context-Free Grammar (CFG) or Probabilistic Context-Free Grammar (PCFG) in Chomsky Normal Form (CNF).
	"""
	
	EPSILON = 'ε'

	def __init__(self, 
		from_dict: dict[str, set[str]|set[tuple[str, int|float]]]|None=None, 
		from_file: str|None=None, 
		from_text: str|None=None, 
		from_words: set[str]|None=None,
		start_symbol: str|None=None, 
		probabilistic: bool|None=None 
		) -> None:
		"""
		Initialize the CFG object with the provided rules.

		The CFG is stored in Chomsky Normal Form (CNF) internally, so the rules are converted to CNF if they are not already in CNF.
		If the provided grammar is probabilistic (PCFG), it should be given in CNF.

		The symbols must be single characters (strings of length 1): uppercase for nonterminal symbols and lowercase or numbers for terminal symbols.

		If the grammar is read from a file or text, the file must contain the rules in the following format:
		- The first line of the file or text must contain only 'CFG' or 'PCFG' to specify the type of the grammar.
		- The start symbol must appear first in the file.
		- For deterministic grammar (CFG), each production must be in the form: Symbol -> Production1 | Production2 | ... | ProductionN
		- For probabilistic grammar (PCFG), each production must be in the form: Symbol -> Production1 [Probability1] | Production2 [Probability2] | ... | ProductionN [ProbabilityN]
		- If the grammar is probabilistic:
			- The probabilities of the productions for each symbol must sum up to 1.
			- The grammar must be in Chomsky Normal Form (CNF).

		Parameters
		----------
		from_dict (dict, optional): A dictionary of rules. 
			For CFG the format must be: {Symbol: {Production1, Production2, ...}, ...}. 
			For PCFG the format must be:{Symbol: {(Production1, Prob(Production1)), (Production2, Prob(Production2)), ...}, ...}.
		from_file (str, optional): The path to the file containing the grammar rules in string format.
		from_text (str, optional): The grammar rules in string format.
		from_words (set, optional): A set of words for which to generate the grammar rules.
		start_symbol (str, optional): The start symbol of the grammar. 
			If not provided, the first symbol is inferred checking all the productions generated by each symbol.
		probabilistic (bool, optional): Whether the grammar is probabilistic or not. This parameter is only used if the rules are provided directly,
			if the rules are read from a file or text, the type of the grammar is inferred from the file or text.

		Initializes the CKY parser with a given Context-Free Grammar (CFG).
		"""
		assert sum(arg is not None for arg in (from_dict, from_file, from_text, from_words)) == 1, \
			"Please provide one (and only one) of the rules, the file path, or the text containing the rules of the grammar."
		assert (probabilistic is not None) if (from_dict is not None) else True, \
			"Please provide the type of the grammar with the parameter 'probabilistic' if the rules are provided directly."
				
		self.start_symbol = start_symbol

		if from_dict is not None: # The only case where the probabilistic parameter is determined by the user
			self.probabilistic = probabilistic

		if (from_file is not None) or (from_text is not None):
			from_dict = self.read_rules_from_file_or_text(file_path=from_file, text=from_text)

		if from_words is not None:
			self.terminals, self.nonterminals = set(), set()
			self.available_nonterminals = self.generate_available_nonterminals()

			if start_symbol is not None:
				warnings.warn("The start symbol is ignored when generating the grammar from words.", UserWarning)
			if probabilistic is True:
				warnings.warn("The grammar is assumed to be deterministic when generating the grammar from words. Ignoring the probabilistic parameter.", UserWarning)

			self.probabilistic = False
			from_dict = self.generate_rules_from_words(words=from_words)

		self.assert_valid_format(from_dict)

		if not self.probabilistic:
			self.rules: dict = from_dict.copy()
		else:
			self.rules, self.probabilities = self.split_probabilities(from_dict)

		self.improve_format()

		self.terminals, self.nonterminals = self.find_symbols(start_symbol=self.start_symbol)

		if self.start_symbol is None:
			self.start_symbol = self.find_start_symbol()

		if from_words is None: # In that case, the available nonterminals are already generated
			self.available_nonterminals = self.generate_available_nonterminals()

		print("\nInitial rules:", self, sep='\n')

		if self.probabilistic:
			assert self.is_cnf(), "The provided PCFG is not in CNF. Please provide a PCFG in CNF."
			self.precomputed_lhs = self.precompute_lhs()
		else:
			if not self.is_cnf():
					warnings.warn("The provided CFG is not in CNF. Converting to CNF. Some productions and symbols may change.", UserWarning)
					self.to_cnf()
					self.precomputed_lhs = self.precompute_lhs()

	def __call__(self, symbol: str) -> list:
		"""
		Allows the CFG object to be called as a function to get the productions for a given symbol.

		Parameters
		----------
		symbol (str): The symbol for which to get the productions.

		Returns
		-------
		list
			List of productions for the given symbol.
		"""
		return self.get_rhs(symbol)
	
	def generate_rules_from_words(self, words: set[str]) -> dict[str, set[str]]:
		"""
		Generates the grammar rules that produce the given set of words.

		Parameters
		----------
		words (set[str]): A set of words for which to generate the grammar.

		Returns
		-------
		dict
			A dictionary of rules in the form of {Symbol: {Production1, Production2, ...}, ...} for a deterministic CFG.
		"""
		assert all(isinstance(word, str) for word in words), "All words must be strings."
		
		# Lowercase the words
		if any(c.isupper() for word in words for c in word):
			warnings.warn("Some words contain uppercase characters. Converting all words to lowercase.", UserWarning)
			words = {word.lower() for word in words}

		self.start_symbol = self.create_nonterminal() # Start symbol is automatically added to nonterminals in create_nonterminal()
		self.terminals = set(sym for word in words for sym in word)

		rules = defaultdict(set)
		for word in words:
			production = ''
			for sym in word:
				nonterminal = self.get_or_create_nonterminal(rhs=sym, rules=rules)
				production += nonterminal
				rules[nonterminal] = {sym}
			rules[self.start_symbol].add(production)

		return dict(rules)
	
	def read_rules_from_file_or_text(self, file_path: str|None=None, text: str|None=None) -> dict[str, set[str]|set[tuple[str, int|float]]]:
		"""
		Reads the grammar rules from a file or string and returns them in the correct format.

		The production rules must be provided in the file in the following format:
		- The first line of the file or text must contain only 'CFG' or 'PCFG' to specify the type of the grammar.
		- Each nonterminal symbol must be a single uppercase character.
		- Each terminal symbol must be a single lowercase character or a number.
		- The start symbol must appear first in the file.
		- For deterministic grammar (CFG), each production must be in the form: Symbol -> Production1 | Production2 | ... | ProductionN
		- For probabilistic grammar (PCFG), each production must be in the form: Symbol -> Production1 [Probability1] | Production2 [Probability2] | ... | ProductionN [ProbabilityN]
		- If the grammar is probabilistic:
			- The probabilities of the productions for each symbol must sum up to 1.
			- The grammar must be in Chomsky Normal Form (CNF).

		Parameters
		----------
		file_path (str, optional): The path to the file containing the grammar rules in string format. Default is None.
		text (str, optional): The grammar rules in string format. Default is None.

		Returns
		-------
		dict
			A dictionary of rules in the form of {Symbol: {Production1, Production2, ...}, ...} for a deterministic CFG.
			A dictionary of rules in the form of {Symbol: {(Production1, Prob(Production1)), (Production2, Prob(Production2)), ...}, ...} for a probabilistic CFG.
		"""
		assert (file_path is None) != (text is None), "Please provide only one of the file path or the text containing the grammar rules."

		self.probabilistic = None

		if file_path is not None:
			if not os.path.exists(file_path):
				raise FileNotFoundError(f"The file '{file_path}' does not exist. Please provide a valid file path for the grammar rules.")
			
			lines = open(file_path, 'r').readlines()
		elif text is not None:
			lines = text.split('\n')

		rules = {}
		
		for line in lines:
			line = line.strip()
			if not line:
				continue
			
			# Infer the type of the grammar
			if self.probabilistic is None:
				if '->' in line:
					raise ValueError("The type of the grammar ('CFG' or 'PCFG') must be specified in the first line of the file or text, before any rules.")
				
				elif 'PCFG' in line:
					self.probabilistic = True
					continue
				
				elif 'CFG' in line:
					self.probabilistic = False

			# Read the rules
			else:
				lhs, rhs = line.split('->')
				lhs = lhs.strip()
				rhs = rhs.strip()

				if self.start_symbol is None:
					self.start_symbol = lhs
				
				rhs = rhs.split('|')
				rhs = {production.strip() for production in rhs}

				if self.probabilistic:
					rhs = {tuple(production.split('[')) for production in rhs}
					rhs = {(production.strip(), float(probability.strip(']').strip())) for production, probability in rhs}

				rules[lhs] = rhs

		return rules

	def assert_valid_format(self, rules) -> None:
		"""
		Asserts that the format of the grammar is valid.

		The grammar must be in the form of a dictionary with the keys as symbols and the values as lists of productions.
		Each symbol must be a string and each production must be a string of symbols.

		Parameters
		----------
		rules (dict): A dictionary of rules. It could be for a deterministic CFG or a probabilistic CFG.

		Raises
		------
		ValueError
			If the grammar is not in the correct format.
		"""
		if not isinstance(rules, dict):
			raise ValueError("The grammar must be provided as a dictionary of rules in the form of {Symbol: {Production1, Production2, ...}, ...}.")
		
		for lhs, rhs in rules.items():
			if not isinstance(lhs, str):
				raise ValueError("All symbols must be strings.")
			if len(lhs) != 1:
				raise ValueError("All symbols must be single characters (strings of length 1).")
			
			if not isinstance(rhs, list|set|tuple):
				raise ValueError("The set of productions for each symbol must be provided as a list, set, or tuple of strings.")
			
			for production in rhs:
				if not self.probabilistic:
					if not isinstance(production, str):
						raise ValueError("All individual productions must be strings.")
				else:
					if not isinstance(production, tuple) or len(production) != 2:
						raise ValueError("All individual productions must be tuples of the form (Production, Probability).")
					if not isinstance(production[0], str):
						raise ValueError("All individual productions must be strings.")
					if not isinstance(production[1], int|float):
						raise ValueError("All individual probabilities must be integers or floats.")
			
			if self.probabilistic:
				prob_sum = sum(probability for _, probability in rhs)
				if prob_sum != 1:
					raise ValueError(f"The probabilities of the productions for each symbol must sum up to 1. For the symbol '{lhs}', the sum is {prob_sum}.")

	def split_probabilities(self, full_rules: dict[str, set[str]]) -> tuple[dict[str, set[str]], dict[str, dict[str, int|float]]]:
		"""
		Splits the full rules of the probabilistic CFG into rules and probabilities.

		Parameters
		----------
		full_rules (dict): A dictionary of rules in the form of {Symbol: {(Production1, Probability(Production1)), (Production2, Probability(Production2)), ...}, ...}.

		Returns
		-------
		tuple[dict, dict]
			A tuple containing the rules and probabilities separately.
		"""
		rules, probabilities = {}, {}
		for lhs, rhs in full_rules.items():
			rules[lhs] = {production for production, _ in rhs}
			probabilities[lhs] = {production: probability for production, probability in rhs}

		return rules, probabilities
	
	def improve_format(self) -> None:
		"""
		Sets the correct format for the grammar for better consistency and easier processing.
		"""
		for lhs, rhs in self.rules.items():
			if not isinstance(rhs, set):
				self.rules[lhs] = set(rhs)
			
			for production in rhs:
				if not isinstance(production, str):
					self.rules[lhs].remove(production)
					self.rules[lhs].add(str(production))
				
				# Replace empty strings with epsilon
				elif production == '':
					self.rules[lhs].remove(production)
					self.rules[lhs].add(self.EPSILON)

				# Remove epsilon from productions of length >= 2 (useless epsilon)
				if len(production) >= 2 and self.EPSILON in production:
					self.rules[lhs].remove(production)
					self.rules[lhs].add(production.replace(self.EPSILON, ''))

	def find_symbols(self, start_symbol: str|None) -> tuple[set, set]:
		"""
		Finds the terminal and nonterminal symbols in the grammar, checks if they are in the correct format, and returns them.

		The terminal symbols are the ones that are only produced and never produce any other symbol,
		while the nonterminal symbols are the ones that produce other symbols and can be produced by other symbols.

		Parameters
		----------
		start_symbol (str, optional): The start symbol specified by the user.

		Returns
		-------
		tuple[set, set]
			A tuple containing the terminal and nonterminal symbols.

		Raises
		------
		ValueError
			If the terminal symbols are not lowercase or the nonterminal symbols are not uppercase.
		ValueError
			If there are symbols that produce other symbols but are not produced by any other symbol (cannot be reached).
		"""
		nonterminals = set(sym for sym in self.rules.keys())

		if any(not symbol.isupper() for symbol in nonterminals):
			raise ValueError("The grammar is not correct. All nonterminal symbols must be uppercase.")

		terminals = set()
		for rhs in self.rules.values():
			for production in rhs:
				for sym in production:
					if sym not in nonterminals:
						terminals.add(sym)

		if not all(symbol.islower() or symbol.isnumeric() for symbol in terminals):
			raise ValueError("The grammar is not correct. All terminal symbols must be lowercase or numbers.")

		if start_symbol is not None:
			value = nonterminals - self.__get_reachable_nonterminals(start_symbol=start_symbol, nonterminals=nonterminals)
			if value:
				print("Not reachable:", value)
				raise ValueError("The grammar is not correct. Some symbols produce other symbols but are not produced by any other symbol (cannot be reached).")

		return terminals, nonterminals
	
	def __get_reachable_nonterminals(self, start_symbol: str, nonterminals: set):
		"""
		Identifies all reachable nonterminals in the grammar.

		Parameters
		----------
		start_symbol (str): The start symbol of the grammar.
		nonterminals (set): The set of nonterminal symbols in the grammar.

		Returns
		-------
		set
			Set of reachable nonterminal symbols.
		"""
		reachable = set()
		to_process = [start_symbol]
		while to_process:
			current = to_process.pop()
			if current not in reachable:
				reachable.add(current)
				for production in self.get_rhs(current):
					for symbol in production:
						if symbol in nonterminals:
							to_process.append(symbol)
		return reachable
	
	def find_start_symbol(self) -> str:
		"""
		Finds the start symbol of the grammar.

		Returns
		-------
		str
			The start symbol of the grammar.

		Raises
		------
		ValueError
			If the start symbol cannot be inferred from the grammar rules.
		"""
		produced_symbols = set()
		for lhs, rhs in self.rules.items():
			for production in rhs:
				for sym in production:
					produced_symbols.add(sym)

		candidates = self.nonterminals - produced_symbols

		if not candidates or len(candidates) > 1:
			raise ValueError("Could not infer the start symbol, more than 1 candidate found. Please provide the start symbol explicitly and ensure that the grammar is correct.")

		start_symbol = candidates.pop() # Get the nonterminal symbol that is not produced by any other symbol

		return start_symbol
	
	def generate_available_nonterminals(self) -> list:
		"""
		Generates a set of available nonterminal symbols that can be used to create new nonterminals.

		Returns
		-------
		list
			Sorted list of available nonterminal symbols (sorted in reverse order for easier access using pop() method).
		"""
		uppercase_abecedary = "SABCDEFGHIJKLMNOPQRTUVWXYZ"
		other_greek_uppercase_letters = "ΓΔΘΛΞΠΣΦΨΩ"
		
		return list(sorted(set(uppercase_abecedary + other_greek_uppercase_letters) - self.nonterminals, reverse=True))
	
	def is_cnf(self) -> bool:
		"""
		Checks if the grammar is in Chomsky Normal Form (CNF).

		A CFG is in CNF if all its rules are of the form:
		- A -> a, where A is a nonterminal symbol and a is a terminal symbol.
		- A -> BC, where A, B, and C are nonterminal symbols.
		- S -> ε, where S is the start symbol and ε is the empty string.

		Returns
		-------
		bool
			True if the grammar is in CNF, False otherwise.
		"""
		for lhs, rhs in self.rules.items():
			for production in rhs:
				if len(production) == 1:
					if not self.is_terminal(production):
						return False
					
					if lhs != self.start_symbol and production == self.EPSILON:
						return False
				
				elif len(production) == 2:
					if any(not self.is_nonterminal(sym) for sym in production):
						return False
				
				else:
					return False
		
		return True
	
	def to_cnf(self) -> None:
		"""
		Converts the grammar to Chomsky Normal Form (CNF).

		A CFG is in CNF if all its rules are of the form:
		- A -> a, where A is a nonterminal symbol and a is a terminal symbol.
		- A -> BC, where A, B, and C are nonterminal symbols and B, C are not the start symbol.
		- S -> ε, where S is the start symbol and ε is the empty string.

		More information: https://en.wikipedia.org/wiki/Chomsky_normal_form
		"""
		self.remove_start_symbol_from_rhs()
		# print("Removed start symbol from RHS:", self)
		self.remove_productions_with_nonsolitary_terminals()
		# print("Removed rules with nonsolitary terminals:", self)
		self.remove_long_nonterminal_productions()
		# print("Removed rules with long nonterminals:", self)
		self.remove_epsilon_productions()
		# print("Removed epsilon rules:", self)
		self.remove_unit_productions()
		# print("Removed unit rules:", self)

		self.assert_valid_format(self.rules)
		
		# Update the symbols and start symbol
		self.terminals, self.nonterminals = self.find_symbols(start_symbol=self.start_symbol)
		self.start_symbol = self.find_start_symbol()

		print("Converted CFG to CNF:", self, sep='\n')

		assert self.is_cnf(), "The CFG could not be converted to CNF successfully."

	def precompute_lhs(self) -> dict[str, str]:
		"""
		Precomputes the left-hand side symbols for the right-hand side productions for faster access.

		Returns
		-------
		dict
			Dictionary of precomputed left-hand side symbols for the right-hand side productions.
		"""
		precomputed_lhs = defaultdict(set)
		for lhs, rhs in self.rules.items():
			for production in rhs:
				precomputed_lhs[production].add(lhs)

		return dict(precomputed_lhs)

	def remove_start_symbol_from_rhs(self) -> None:
		"""
		Removes the start symbol from the right-hand side of the rules.
		"""
		self.original_start_symbol = self.start_symbol

		new_start_symbol = self.create_nonterminal()
		self.rules[new_start_symbol] = {self.start_symbol}
		self.nonterminals.add(new_start_symbol)
		
		self.start_symbol = new_start_symbol
		
	def remove_productions_with_nonsolitary_terminals(self) -> None:
		"""
		Removes the productions that contain nonsolitary terminal symbols.
		"""
		new_rules = {}
		new_nonterminals = set()
		for lhs, rhs in self.rules.items():
			new_rhs = set()
			for production in rhs:
				# Contains nonsolitary terminal symbols
				if any(self.is_terminal(sym) for sym in production) and len(production) > 1:
					new_production = ''
					for sym in production:
						# Is a nonsolitary terminal symbol
						if self.is_terminal(sym):
							new_nt = self.get_or_create_nonterminal(rhs=sym, rules=new_rules)
							new_production += new_nt
							new_rules[new_nt] = {sym}
							new_nonterminals.add(new_nt)

						# Is a nonterminal symbol
						else:
							new_production += sym
					new_rhs.add(new_production)

				# Does not contain nonsolitary terminal symbols
				else:
					new_rhs.add(production)	
		
			new_rules[lhs] = new_rhs
		
		self.rules = new_rules
		self.nonterminals.update(new_nonterminals)

	def remove_long_nonterminal_productions(self) -> None:
		"""
		Removes the productions that contain more than two nonterminal symbols.
		"""
		new_rules = {}
		new_nonterminals = set()
		for lhs, rhs in self.rules.items():
			new_rhs = set()
			for production in rhs:
				# Contains long nonterminal symbols
				if len(production) > 2:
					new_production = production
					while len(new_production) > 2:
						# Get the first two symbols (nonterminals) and create a new symbol that produces them
						first, second = new_production[:2]
						new_nt = self.get_or_create_nonterminal(rhs=first + second, rules=new_rules)
						new_production = new_nt + new_production[2:]
						new_rules[new_nt] = {first + second}
						new_nonterminals.add(new_nt)
					
					new_rhs.add(new_production)

				# Does not contain long nonterminal symbols
				else:
					new_rhs.add(production)

			new_rules[lhs] = new_rhs

		self.rules = new_rules
		self.nonterminals.update(new_nonterminals)

	def remove_epsilon_productions(self) -> None:
		"""
		Removes the epsilon productions from the grammar.
		"""
		nullable = self.get_nullable_nonterminals()

		new_rules = defaultdict(set)
		for lhs, rhs in self.rules.items():
			for production in rhs:
				if production != self.EPSILON:
					new_rules[lhs].add(production)
					indices = [i for i, sym in enumerate(production) if sym in nullable]
					for n in range(1, len(indices) + 1):
						for comb in combinations(indices, n):
							new_production = ''.join(sym for i, sym in enumerate(production) if i not in comb)
							if new_production == '':
								new_production = self.EPSILON
							new_rules[lhs].add(new_production)
				elif lhs == self.start_symbol:
					new_rules[lhs].add(self.EPSILON)

		self.rules = dict(new_rules)

	def get_nullable_nonterminals(self) -> set:
		"""
		Identifies all nullable nonterminals in the grammar.

		If a rule A --> ε exists, then A is nullable.
		If a rule A --> X1 ... Xn exists, and every single Xi is nullable, then A is nullable too.

		Returns
		-------
		set
			Set of nullable nonterminal symbols.
		"""
		nullable = set(lhs for lhs, rhs in self.rules.items() if self.EPSILON in rhs)

		changed = True
		while changed:
			changed = False
			for lhs, rhs in self.rules.items():
				if lhs in nullable:
					continue
				for production in rhs:
					if all(sym in nullable or sym == lhs for sym in production):
						nullable.add(lhs)
						changed = True
						break
		return nullable
	
	def remove_unit_productions(self) -> None:
		"""
		Removes the unit nonterminal productions from the grammar.
		"""
		unit_pairs = set()  # Set of (A, B) pairs where A -> B is a unit production
		
		# Find all unit pairs
		for lhs, rhs in self.rules.items():
			for production in rhs:
				if len(production) == 1 and self.is_nonterminal(production):
					unit_pairs.add((lhs, production))

		# Find the transitive closure of the unit pairs
		while True:
			new_pairs = set()
			for (A, B) in unit_pairs:
				for (C, D) in unit_pairs:
					if B == C:
						new_pairs.add((A, D))
			if new_pairs.issubset(unit_pairs):
				break
			unit_pairs.update(new_pairs)

		# Add new productions for each unit pair
		new_rules = defaultdict(set)
		for lhs, rhs in self.rules.items():
			for production in rhs:
				if len(production) != 1 or not self.is_nonterminal(production):
					new_rules[lhs].add(production)
		for (A, B) in unit_pairs:
			if A != B:
				for production in self.rules.get(B, set()):
					if len(production) != 1 or not self.is_nonterminal(production):
						new_rules[A].add(production)

		self.rules = dict(new_rules)

		# Remove nonterminals that are not produced anywhere
		produced_symbols = set()
		for rhs in self.rules.values():
			for production in rhs:
				for sym in production:
					produced_symbols.add(sym)
		unused_nonterminals = self.nonterminals - produced_symbols - {self.start_symbol}
		for nonterminal in unused_nonterminals:
			self.remove_rule(nonterminal)
		self.nonterminals -= unused_nonterminals

	def create_nonterminal(self) -> str:
		"""
		Helper function to create a new nonterminal symbol.
		"""
		assert self.available_nonterminals, "The grammar has run out of nonterminal symbols."
		
		new_nt = self.available_nonterminals.pop()
		self.nonterminals.add(new_nt)
		return new_nt
	
	def get_or_create_nonterminal(self, rhs: set|str, rules: dict[str, set[str]]|None=None) -> str:
		"""
		Helper function to get an existing nonterminal symbol or create a new one if it does not exist.

		Parameters
		----------
		rhs (set|str): The right-hand side of the production. If it is a str, it is converted to a set(str).
		rules (dict, optional): The rules of the grammar. If not provided, the rules of the current grammar are used.

		Returns
		-------
		str
			The existing or new nonterminal symbol that produces the given production.
		"""
		if isinstance(rhs, str):
			rhs = {rhs}

		existing_nt = self.get_lhs(produced_rhs=rhs, rules=rules, exact_match=True)
		
		if existing_nt is None:
			new_nt = self.create_nonterminal()
			return new_nt
		
		return existing_nt
	
	def remove_rule(self, lhs: str) -> None:
		"""
		Removes a rule from the grammar.

		Parameters
		----------
		lhs (str): The left-hand side of the rule to remove.
		"""
		self.rules.pop(lhs, None)

	def is_probabilistic(self) -> bool:
		"""
		Checks if the grammar is probabilistic (PCFG).

		Returns
		-------
		bool
			True if the grammar is probabilistic, False otherwise.
		"""
		return self.probabilistic
	
	def is_terminal(self, symbol: str) -> bool:
		"""
		Checks if a given symbol is a terminal symbol in the grammar.

		Parameters
		----------
		symbol (str): The symbol to check.

		Returns
		-------
		bool
			True if the symbol is a terminal symbol, False otherwise.
		"""
		return symbol in self.terminals
	
	def is_nonterminal(self, symbol: str) -> bool:
		"""
		Checks if a given symbol is a nonterminal symbol in the grammar.

		Parameters
		----------
		symbol (str): The symbol to check.

		Returns
		-------
		bool
			True if the symbol is a nonterminal symbol, False otherwise.
		"""
		return symbol in self.nonterminals
	
	def get_start_symbol(self) -> str:
		"""
		Returns the start symbol of the grammar.

		Returns
		-------
		str
			The start symbol of the grammar.
		"""
		return self.start_symbol

	def get_terminal_symbols(self) -> set:
		"""
		Returns the set of terminal symbols in the grammar.

		Returns
		-------
		set
			Set of terminal symbols.
		"""
		return self.terminals
	
	def get_nonterminal_symbols(self) -> set:
		"""
		Returns the set of nonterminal symbols in the grammar.

		Returns
		-------
		set
			Set of nonterminal symbols.
		"""
		return self.nonterminals
	
	def get_rhs(self, symbol: str) -> list:
		"""
		Returns the list of productions for a given symbol.

		Parameters
		----------
		symbol (str): The symbol for which to get the productions.

		Returns
		-------
		list
			List of productions for the given symbol.
		"""
		return self.rules.get(symbol, [])
	
	def get_probability(self, lhs: str, production: str) -> int|float:
		"""
		Returns the probability of a given production for a given symbol.

		Parameters
		----------
		lhs (str): The left-hand side of the production.
		production (str): The production produced by the left-hand side symbol.

		Returns
		-------
		int|float
			The probability of the production for the given symbol.
		"""
		return self.probabilities.get(lhs, {}).get(production, 0)
	
	def get_lhs(self, produced_rhs: set|str, rules: dict[str, set[str]]|None=None, exact_match: bool=True) -> None|str|set[str]:
		"""
		Returns the symbol exactly produces the given production.

		Parameters
		----------
		produced_rhs (set|str): The production to find the symbol for. If it is a str, it is converted to a set(str).
		rules (dict, optional): The rules of the grammar. If not provided, the rules of the current grammar are used.
		exact_match (bool): Whether to find the exact match or the subset match. Default is True.

		Returns
		-------
		None|str|set
			The symbol that produces the given production. None if the production is not found.
			If exact_match is False, a set of symbols that produce the given production is returned.
		"""
		if isinstance(produced_rhs, str):
			produced_rhs = {produced_rhs}

		rules = rules if rules is not None else self.rules

		if exact_match:
			for lhs, rhs in rules.items():
				if produced_rhs == rhs:
					return lhs

		else:
			matches = set()
			for lhs, rhs in rules.items():
				if produced_rhs.issubset(rhs):
					matches.add(lhs)
			
			return matches
		
		return None
	
	def get_precomputed_lhs(self) -> dict[str, str]:
		"""
		Returns the precomputed left-hand side symbols for the right-hand side productions.

		Returns
		-------
		dict
			Dictionary of precalculated left-hand side symbols for the right-hand side productions.
		"""
		return self.precomputed_lhs
	
	def get_rules(self) -> dict[str, set[str]]:
		"""
		Returns the rules of the grammar.

		Returns
		-------
		dict
			Dictionary of rules in the form of {Symbol: {Production1, Production2, ...}, ...}.
		"""
		return self.rules
	
	def get_probabilities(self) -> dict[str, dict[str, int|float]]:
		"""
		Returns the probabilities of the grammar if it is probabilistic.

		Returns
		-------
		dict
			Dictionary of probabilities in the form of {Symbol: {Production1: Prob(Production1), Production2: Prob(Production2), ...}, ...}.
		"""
		assert self.probabilistic, "The grammar is not probabilistic. No probabilities available."

		return self.probabilities
	
	def set_rules(self, *args: Any, **kwargs: Any) -> None:
		"""
		Sets the rules of the grammar.

		Parameters
		----------
		*args: Arguments to pass to the __init__ method.
		**kwargs: Keyword arguments to pass to the __init__ method.
		"""
		self.__init__(*args, **kwargs)

	def generate_words(self, max_length: int, round_probabilities: bool=False) -> list:
		"""
		Generates all possible words up to a certain length that can be generated by the grammar.
		If the grammar is probabilistic (PCFG), the words are returned with their total probability of being generated 
		(sum of all the probabilities of the different paths to the same word).

		Warning: Large values of max_length may take a long time to generate all possible words and consume a lot of memory, 
		especially for probabilistic grammars (PCFG).

		Parameters
		----------
		max_length (int): The maximum length of the words to generate.
		round_probabilities (bool): Whether to use dynamic rounding for the probabilities (with default theshold) or not. Default is False.
			This helps fixing the floating point errors in the probabilities.

		Returns
		-------
		list
			List of words that can be generated by the grammar up to the maximum length.
			The list is sorted in lexicographical order if the grammar is deterministic (CFG).
			The list is sorted by the total probability of each word if the grammar is probabilistic (PCFG).
		"""
		assert max_length >= 0, "The maximum length must be greater than 0."
		if max_length > 8:
			warnings.warn("Large values of max_length may take a long time to generate all possible words and consume a lot of memory.", UserWarning)

		if max_length == 0:
			return [self.EPSILON] if self.is_terminal(self.EPSILON) else []

		num_generated_words = 0
		if self.probabilistic:
			words_with_probabilities = {}
		else:
			visited = set()
			words = set()
		
		# Queue of (current_string, current_probability), 
		# where current_string is the current string being processed,
		# and current_probability is the probability of the word so far
		queue = deque([(self.start_symbol, 1.0)]) 

		while queue:
			current_string, current_probability = queue.popleft()

			# If the current word exceeds the maximum length, skip it
			if len(current_string) > max_length:
				continue

			# If current_string is fully expanded (all terminals), add to words
			if all(self.is_terminal(sym) for sym in current_string):
				if len(current_string) <= max_length:
					if self.probabilistic:
						if current_string in words_with_probabilities:
							words_with_probabilities[current_string] += current_probability # Sum the probabilities of the same word (all different paths to the same word)
						else:
							words_with_probabilities[current_string] = current_probability
							num_generated_words += 1
					
					else:
						words.add(current_string)
						num_generated_words += 1

					print(f"Number of words generated: {num_generated_words}", end='\r')
				continue

			# Process each symbol in the current string
			for i, sym in enumerate(current_string):
				if self.is_nonterminal(sym):
					for production in self.rules[sym]:
						new_string = current_string[:i] + production + current_string[i+1:]
						new_probability = current_probability * self.get_probability(sym, production) if self.probabilistic else 1.0
						
						if len(new_string) <= max_length:
							if self.probabilistic:
								# No pruning for probabilistic grammars (because all the probabilities must be summed up)
								queue.append((new_string, new_probability))
							else:
								# Prune the visited words
								if new_string not in visited: 
									visited.add(new_string)
									queue.append((new_string, new_probability))
					break  # Only expand the first nonterminal symbol, to avoid visiting the same word multiple times

		print()

		if self.probabilistic and round_probabilities:
			for word in words_with_probabilities:
				words_with_probabilities[word] = dynamic_round(words_with_probabilities[word])

		return sorted([(word, prob) for word, prob in words_with_probabilities.items()], key=lambda x: x[1], reverse=True) if self.probabilistic else sorted(words)

	def __str__(self) -> str:
		"""
		Returns a string that represents the CFG object in a readable format.

		The representation includes the rules, start symbol, terminal symbols, and nonterminal symbols, all sorted in an understandable way.

		Returns
		-------
		str
			String showing the CFG object in a readable format.
		"""
		produced_by_start = {production for production in self.get_rhs(self.start_symbol) if production in self.nonterminals}
		nonterminals_order = [self.start_symbol] + [*produced_by_start] + list(sorted(self.nonterminals - {self.start_symbol} - produced_by_start))
		terminals_string = ', '.join(sorted(self.terminals))
		nonterminals_string = ', '.join(nonterminals_order)
		
		if not self.probabilistic:
			dict_string = '\n'.join(f"\t{lhs} -> {' | '.join(sorted(rhs))}" for lhs, rhs in zip(nonterminals_order, [self.get_rhs(nt) for nt in nonterminals_order]))
			
			return f"CFG(\n{dict_string}\n)\n" \
				f"\n* Start Symbol: {self.start_symbol}" \
				f"\n* Terminal Symbols: {{{terminals_string}}}" \
				f"\n* Non-Terminal Symbols: {{{nonterminals_string}}}\n"
		else:
			rules_strings = []
			sorted_tuples = [(lhs, rhs) for lhs, rhs in zip(nonterminals_order, [self.get_rhs(nt) for nt in nonterminals_order])]
			for lhs, rhs in sorted_tuples:
				rules_strings.append(f"\t{lhs} -> {' | '.join(f'{production} [{self.get_probability(lhs, production)}]' for production in sorted(rhs))}")
			dict_string = '\n'.join(rules_strings)

			return f"PCFG(\n{dict_string}\n)\n" \
				f"\n* Start Symbol: {self.start_symbol}" \
				f"\n* Terminal Symbols: {{{terminals_string}}}" \
				f"\n* Non-Terminal Symbols: {{{nonterminals_string}}}\n"
