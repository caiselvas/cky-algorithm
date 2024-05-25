import matplotlib.pyplot as plt
import networkx as nx
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
	>>> custom_round(3.14159, 3)
	3.14159
	>>> custom_round(0.0005163749999999999, 3)
	0.000516375
	>>> custom_round(2.2680000000000003e-05, 3)
	2.268e-05
	"""
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

def transform_probabilistic_to_deterministic(parse_trees_with_probs) -> tuple[float, list]:
	"""
	Transforms a list of parse trees with their probabilities to a list of parse trees without probabilities.

	Parameters
	----------
	parse_trees_with_probs (list): A list of tuples with parse trees and their probabilities.

	Returns
	-------
	tuple[float, list]
		The total probability of the parse trees and the parse trees without probabilities as a list.
	"""
	total_prob = sum(prob for _, prob in parse_trees_with_probs)
	
	def remove_probs(node):
		if isinstance(node, tuple) and len(node) > 1:
			return tuple(remove_probs(child) for child in node if not isinstance(child, float))
		return node

	parse_trees_deterministic = [remove_probs(tree) for tree, _ in parse_trees_with_probs]
	
	return total_prob, parse_trees_deterministic

def visualize_parse_trees(parse_trees_with_probs: list, prob: bool = True) -> None:
	"""
	Visualizes the parse trees with their probabilities using networkx and matplotlib.

	Parameters
	----------
	parse_trees_with_probs (list): A list of tuples with parse trees and their probabilities.
	prob (bool): Whether the parse trees are probabilistic. Default is True.
	"""
	def add_nodes_edges(tree, graph: nx.DiGraph, parent: str|None = None, order: list = [0], layer: int = 0, idx: int = 0):
		"""
		Recursively adds nodes and edges to the networkx DiGraph.

		Parameters
		----------
		tree (Any): The current subtree.
		graph (nx.DiGraph): The networkx DiGraph object.
		parent (str, optional): The parent node identifier.
		order (list): A list containing a single integer to keep track of the order of edges.
		layer (int): The current layer of the node.
		idx (int): The index of the current tree to ensure unique node identifiers.
		"""
		if isinstance(tree, tuple) and len(tree) == 3:
			symbol, left, right = tree
			node_id = f'{symbol}_{id(tree)}_{idx}'
			graph.add_node(node_id, label=symbol, layer=layer)
			
			if parent:
				order[0] += 1
				graph.add_edge(parent, node_id, label=f'{order[0]}')
			
			add_nodes_edges(left, graph, node_id, order, layer + 1, idx)
			add_nodes_edges(right, graph, node_id, order, layer + 1, idx)
		
		elif isinstance(tree, tuple) and len(tree) == 2:
			symbol, terminal = tree
			node_id = f'{symbol}_{id(tree)}_{idx}'
			graph.add_node(node_id, label=symbol, layer=layer)
			
			if parent:
				order[0] += 1
				graph.add_edge(parent, node_id, label=f'{order[0]}')
			
			terminal_id = f'{terminal}_{id(tree)}_{idx}'
			graph.add_node(terminal_id, label=terminal, layer=layer + 1)
			graph.add_edge(node_id, terminal_id, label=f'{order[0]}')
		
		else:
			node_id = f'{tree}_{id(tree)}_{idx}'
			graph.add_node(node_id, label=str(tree), layer=layer)
			
			if parent:
				order[0] += 1
				graph.add_edge(parent, node_id, label=f'{order[0]}')

	graph = nx.DiGraph()
	pos = {}
	y_offset = 0

	total_prob = None
	if prob:
		total_prob, parse_trees_with_probs = transform_probabilistic_to_deterministic(parse_trees_with_probs)
	
	for idx, item in enumerate(parse_trees_with_probs):
		tree = item
		root_id = f'{tree[0]}_{id(tree)}_{idx}'
		root_label = tree[0]
		graph.add_node(root_id, label=root_label, layer=0)

		add_nodes_edges(tree, graph, root_id, [0], 1, idx)

		subtree_pos = nx.multipartite_layout(graph, subset_key='layer')
		subtree_pos = {k: (x, y + y_offset) for k, (x, y) in subtree_pos.items()}
		pos.update(subtree_pos)
		y_offset -= 3

	labels = nx.get_node_attributes(graph, 'label')
	edge_labels = nx.get_edge_attributes(graph, 'label')
	
	plt.figure(figsize=(20, 12))
	nx.draw(graph, pos, labels=labels, with_labels=True, node_size=3000, node_color='lightblue', font_size=10, font_weight='bold', arrows=True, arrowsize=20)
	nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels, font_size=10, font_color='red')
	
	title = 'Parse Trees'
	if prob:
		title = f'Parse Trees with Total Probability {total_prob:.4f}'
	
	plt.title(title)
	plt.show()

def split_input(file_path: str) -> tuple[str, list[str]]:
	"""
	Splits the grammar text and the words to parse from a file.

	Parameters
	----------
	file_path (str): The path to the file containing the grammar and the words to parse.

	Returns
	-------
	tuple[str, list[str]]
		The grammar text and the words to parse.
	"""
	if not os.path.isfile(file_path):
		raise FileNotFoundError(f"File '{file_path}' not found. Please provide a valid file path to get the grammar and the words to parse.")
	
	lines = open(file_path, 'r').readlines()
	
	rules_text, words_text = '', ''
	rules_started, rules_ended = False, False

	for line in lines:
		line = line.strip()
		if not line:
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
