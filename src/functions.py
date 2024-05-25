import matplotlib.pyplot as plt
import networkx as nx


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

def visualize_parse_trees(parse_trees_with_probs: list, prob: bool = True):
    """
    Visualizes the parse trees with their probabilities using networkx and matplotlib.

    Parameters
    ----------
    parse_trees_with_probs : list
        A list of tuples with parse trees and their probabilities.
    filename : str
        The name of the file to save the visualization. Default is 'parse_trees'.
    prob : bool
        Whether the parse trees are probabilistic. Default is True.
    """
    def add_nodes_edges(tree, graph: nx.DiGraph, parent: str = None, order: list = [0], layer: int = 0):
        """
        Recursively adds nodes and edges to the networkx DiGraph.

        Parameters
        ----------
        tree : Any
            The current subtree.
        graph : nx.DiGraph
            The networkx DiGraph object.
        parent : str
            The parent node identifier.
        order : list
            A list containing a single integer to keep track of the order of edges.
        layer : int
            The current layer of the node.
        """
        if isinstance(tree, tuple) and len(tree) == 3:
            symbol, left, right = tree
            node_id = f'{symbol}_{id(tree)}'
            graph.add_node(node_id, label=symbol, layer=layer)
            if parent:
                order[0] += 1
                graph.add_edge(parent, node_id, label=f'{order[0]}')
            add_nodes_edges(left, graph, node_id, order, layer + 1)
            add_nodes_edges(right, graph, node_id, order, layer + 1)
        elif isinstance(tree, tuple) and len(tree) == 2:
            symbol, terminal = tree
            node_id = f'{symbol}_{id(tree)}'
            graph.add_node(node_id, label=symbol, layer=layer)
            if parent:
                order[0] += 1
                graph.add_edge(parent, node_id, label=f'{order[0]}')
            terminal_id = f'{terminal}_{id(tree)}'
            graph.add_node(terminal_id, label=terminal, layer=layer + 1)
            graph.add_edge(node_id, terminal_id, label=f'{order[0]}')
        else:
            node_id = f'{tree}_{id(tree)}'
            graph.add_node(node_id, label=str(tree), layer=layer)
            if parent:
                order[0] += 1
                graph.add_edge(parent, node_id, label=f'{order[0]}')

    for idx, item in enumerate(parse_trees_with_probs):
        if prob:
            tree, tree_prob = item
        else:
            tree, tree_prob = item, None
        
        graph = nx.DiGraph()
        root_id = f'{tree[0]}_{id(tree)}'
        graph.add_node(root_id, label=tree[0], layer=0)
        add_nodes_edges(tree, graph, root_id, [0], 1)  # Reset order for each tree and start layer at 1

        pos = nx.multipartite_layout(graph, subset_key='layer')  # Disposición jerárquica
        labels = nx.get_node_attributes(graph, 'label')
        edge_labels = nx.get_edge_attributes(graph, 'label')
        plt.figure(figsize=(12, 8))
        nx.draw(graph, pos, labels=labels, with_labels=True, node_size=3000, node_color='lightblue', font_size=10, font_weight='bold', arrows=True, arrowsize=20)
        nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels, font_size=10, font_color='red')
        if prob:
            plt.title(f'Parse Tree {idx + 1} with Probability {tree_prob:.4f}')
        else:
            plt.title(f'Parse Tree {idx + 1}')
        plt.show()
