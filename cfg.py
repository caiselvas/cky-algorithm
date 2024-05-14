from typing import Any, Self
import warnings

class CFG:
	"""
	A class to represent a Context-Free Grammar (CFG) and provide methods to work with it.
	"""
	def __init__(self, rules: dict) -> None:
		"""
		Initializes the CKY parser with a given Context-Free Grammar (CFG).

		The CFG is stored in Chomsky Normal Form (CNF) internally, so the rules are converted to CNF if they are not already in CNF.

		Parameters
		----------
		rules (dict): A dictionary of rules in the form of {Symbol: [Production1, Production2, ...]}.
		"""
		self.rules: dict = rules
		self.terminals, self.non_terminals = self.find_symbols()

		if not self.check_cnf():
			self.to_cnf()
			warnings.warn("The provided CFG is not in CNF. Converted to CNF. Some rules and symbols may have changed.", UserWarning)

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
		return self.get_rule(symbol)

	def find_symbols(self) -> tuple[set, set]:
		"""
		Finds the terminal and non-terminal symbols in the grammar.

		Returns
		-------
		tuple[set, set]
			A tuple containing the terminal and non-terminal symbols.
		"""
		non_terminals = set(char for char in ''.join(self.rules.keys()))

		terminals = set()
		for productions in self.rules.values():
			for production in productions:
				for char in production:
					if char not in non_terminals:
						terminals.add(char)

		return terminals, non_terminals
	
	def check_cnf(self) -> bool:
		"""
		Checks if the grammar is in Chomsky Normal Form (CNF).

		A CFG is in CNF if all its rules are of the form:
		- A -> a, where A is a non-terminal symbol and a is a terminal symbol.
		- A -> BC, where A, B, and C are non-terminal symbols.

		Returns
		-------
		bool
			True if the grammar is in CNF, False otherwise.
		"""
		for symbol, productions in self.rules.items():
			for production in productions:
				if len(production) == 1:
					if not self.is_terminal(production):
						return False
				
				elif len(production) == 2:
					if any(not self.is_non_terminal(char) for char in production):
						return False
				
				else:
					return False
		
		return True
	
	def to_cnf(self) -> None:
		"""
		Converts the grammar to Chomsky Normal Form (CNF).

		A CFG is in CNF if all its rules are of the form:
		- A -> a, where A is a non-terminal symbol and a is a terminal symbol.
		- A -> BC, where A, B, and C are non-terminal symbols.
		"""		
		pass
	
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
	
	def is_non_terminal(self, symbol: str) -> bool:
		"""
		Checks if a given symbol is a non-terminal symbol in the grammar.

		Parameters
		----------
		symbol (str): The symbol to check.

		Returns
		-------
		bool
			True if the symbol is a non-terminal symbol, False otherwise.
		"""
		return symbol in self.non_terminals

	def get_terminal_symbols(self) -> set:
		"""
		Returns the set of terminal symbols in the grammar.

		Returns
		-------
		set
			Set of terminal symbols.
		"""
		return self.terminals
	
	def get_non_terminal_symbols(self) -> set:
		"""
		Returns the set of non-terminal symbols in the grammar.

		Returns
		-------
		set
			Set of non-terminal symbols.
		"""
		return self.non_terminals
	
	def get_rule(self, symbol: str) -> list:
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
	
	def get_rules(self) -> dict:
		"""
		Returns the rules of the grammar.

		Returns
		-------
		dict
			Dictionary of rules in the form of {Symbol: [Production1, Production2, ...]}.
		"""
		return self.rules
	
	def set_rules(self, rules: dict) -> None:
		"""
		Sets the rules of the grammar.

		Parameters
		----------
		rules (dict): A dictionary of rules in the form of {Symbol: [Production1, Production2, ...]}.
		"""
		self.__init__(rules)
	
	def add_rule(self, symbol: str, production: str) -> None:
		"""
		Adds a rule to the grammar. If the symbol already exists, the production is appended to its list of productions.

		Parameters
		----------
		symbol (str): The symbol to which the production belongs.
		production (str): The production to be added.
		"""
		if symbol not in self.rules:
			self.rules[symbol] = []
		
		self.rules[symbol].append(production)

		self.terminals, self.non_terminals = self.find_symbols()

	def remove_rule(self, symbol: str, production: str) -> None:
		"""
		Removes a rule from the grammar.

		Parameters
		----------
		symbol (str): The symbol from which the production is to be removed.
		production (str): The production to be removed.
		"""
		assert symbol in self.rules, f"Symbol '{symbol}' not found in the grammar."

		self.rules[symbol].remove(production)

		self.terminals, self.non_terminals = self.find_symbols()
		self.is_cnf = self.check_cnf()

	def __repr__(self) -> str:
		"""
		Creates a string representation of the CFG object.

		Returns
		-------
		str
			String representation of the CFG object.
		"""
		return f"CFG({self.rules})"