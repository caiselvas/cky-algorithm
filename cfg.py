class CFG:
	"""
	A class to represent a Context-Free Grammar (CFG) and provide methods to work with it.
	"""
	def __init__(self, rules: dict, terminals: set|None=None, non_terminals: set|None=None) -> None:
		"""
		Initializes the CKY parser with a given Context-Free Grammar (CFG).

		Parameters
		----------
		rules (dict): A dictionary of rules in the form of {Symbol: [Production1, Production2, ...]}.
		terminals (set): A set of terminal symbols. If None, the terminal symbols are inferred from the rules.
		non_terminals (set): A set of non-terminal symbols. If None, the non-terminal symbols are inferred from the rules.
		"""
		assert (terminals is None) == (non_terminals is None), "Both terminals and non-terminals must be provided or omitted."
		
		if terminals is None or non_terminals is None:
			terminals, non_terminals = self.find_symbols()
		
		self.rules: dict = rules
		self.terminals: set = terminals
		self.non_terminals: set = non_terminals

		self.is_cnf: bool = self.check_cnf()

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
	
	def to_cnf(self) -> dict:
		"""
		Returns the Chomsky Normal Form (CNF) representation of the CFG.

		Returns
		-------
		dict
			Dictionary of rules in CNF.
		"""
		if self.is_cnf:
			return self.rules
		
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
		self.is_cnf = self.check_cnf()

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