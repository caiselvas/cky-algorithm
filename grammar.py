

class Grammar:
	def __init__(self, rules: dict, terminals: set|None=None, non_terminals: set|None=None) -> None:
		"""
		Initializes the CKY parser with a given Context-Free Grammar (CFG).

		Parameters
		----------
		rules (dict): A dictionary of rules in the form of {Symbol: [Production1, Production2, ...]}.
		terminals (set): A set of terminal symbols. If None, the terminal symbols are inferred from the rules.
		non_terminals (set): A set of non-terminal symbols. If None, the non-terminal symbols are inferred from the rules.
		"""
		self.rules: dict = rules
		self.terminals: set = terminals if terminals is not None else self.__find_terminals()
		self.non_terminals: set = non_terminals if non_terminals is not None else self.__find_non_terminals()

	def __find_terminals(self) -> set:
		"""
		Finds terminal symbols in the rules of the grammar.

		Returns
		-------
		set
			A set of terminal symbols.	
		"""
		pass

	def __find_non_terminals(self) -> set:
		"""
		Finds non-terminal symbols in the rules of the grammar.

		Returns
		-------
		set
			A set of non-terminal symbols.
		"""
		pass

	def get_terminal_symbols(self) -> set:
		"""
		Returns a set of terminal symbols in the grammar.

		Returns
		-------
		set
			A set of terminal symbols.
		"""
		pass