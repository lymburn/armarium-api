"""
Final chosen outfit generation algorithm
- Path search:
    - Bellman ford
    - Optimization on default NetworkX Bellman Ford:
        - Take best outfit based on path length, rmv that outfit from the graph, search again. Repeat "n" times
        - This is an attempt to balance getting more good outfits and getting a diverse range of outfits
"""
import networkx as nx
import itertools
import time
from ml.outfit_grader import get_outfit_score

def generate_all_combos(ls):
    # ls = [[], [], ...]
    # https://stackoverflow.com/questions/798854/all-combinations-of-a-list-of-lists
    output = list(itertools.product(*ls))
    return output

# Path search
def bellman_ford_search_best_path_len(graph, clothes, num):
    tik = time.perf_counter()
    srcs = generate_all_combos([clothes['top'], clothes['bottom']])
    targets = clothes['accessory']

    # in the case of a small graph, don't do the variety optimization
    # someone send help, how to do this beautifully :(
    small_graph = False
    num_items = [len(x) for x in clothes.values()]
    for y in num_items:
        if y <= 3:
            small_graph = True
            break

    def find_best_path(src):
        # Targets = all nodes in last category
        # Find path from src to all targets then eval for best scoring outfit
        t_outs = [] # [(length of path, [outfit])]
        for t in targets:
            length, path = nx.single_source_bellman_ford(graph, src, t) # path = [(), , ]
            out = list(path[0]) + path[1:] # Converts path to [, ,]
            t_outs.append((length, out))
        t_outs.sort() # Ascending b/c negative scores
        return t_outs[0][1] # []

    def rmv_best_path(best_path):
        # Given a list of nodes that rep a best path, rmv edges connecting these
        # nodes from the graph + return list of removed edges
        # TODO: Find a more idiomatic / pythonic way to do this

        # Best path = [items]. Need [(tb), s, g, a], knowing structure of v2
        best = [(best_path[0], best_path[1])] + best_path[2:]
        removed_edges = []
        for i in range(len(best)-1):
            w = graph.get_edge_data(best[i], best[i+1])
            removed_edges.append((best[i], best[i+1], w['weight']))
            graph.remove_edge(best[i], best[i+1])
        return removed_edges

    def restore_deleted_edges(rmv_edges):
        # Restore graph
        for set_de in deleted_edges:
            for de in set_de:
                graph.add_edge(de[0], de[1], weight=de[2])

    valid_outfits = []

    if small_graph:
        for s in srcs:
            s_best = find_best_path(s) # Output: (score, [outfit items])
            valid_outfits.append(s_best) 
    else:
        # Repeatedly search, restoring graph aft searching a source
        for s in srcs:
            deleted_edges = []
            for _ in itertools.repeat(None, num):
                # Given a src, find best outfit, rmv edges, repeat num times
                s_best = find_best_path(s) # Output: (score, [outfit items])
                valid_outfits.append(s_best)
                deleted_edges.append(rmv_best_path(s_best))
            restore_deleted_edges(deleted_edges)    

    tok = time.perf_counter()
    print(f"Semicombined (2 categ) directed graph path search for bests based on path length took {tok-tik:0.4f} seconds")
    return valid_outfits

# Evaluating search outputs
def take_best_path_length_outfits(graph, outfit_list, combo=0, num=50):
    # Given a list of outfits found using some algorithm, return top <num> outfits based on path length
    # Output [[outfit]]
    paths_outfits = []
    if combo == 3:
        paths_outfits = [(nx.bellman_ford_path_length(graph, (out[0], out[1], out[3]), out[4]), out) for out in outfit_list]
    elif combo == 2:
        paths_outfits = [(nx.bellman_ford_path_length(graph, (out[0], out[1]), out[4]), out) for out in outfit_list]
    else:
        paths_outfits = [(nx.bellman_ford_path_length(graph, out[0], out[4]), out) for out in outfit_list]
    
    paths_outfits.sort()
    sorted_outfits = [outfit[1] for outfit in paths_outfits]

    return sorted_outfits[:num]

def score_final_outfits_in_descending(outfit_list):
    # Where outfit_list = [[outfit1 items], [outfit2 items], ...]
    # Copy of score_outfits_in_descending but w prints
    # so that the other function can still be used during path search

    score_dict = dict()
    for outfit in outfit_list:
        score = get_outfit_score(outfit)
        score_dict[float(score)] = outfit

    sorted_list = sorted(score_dict.items(), reverse=True)

    return sorted_list

# clothes is a dictionary where the keys are the clothing categories
# and the value is a list of the node names of the items 
def get_top_outfits(graph, clothes, num=5):
    # top_imgs, bottom_imgs, and accessory_imgs are node names that are used to do optimized search
	outfit_list = bellman_ford_search_best_path_len(graph, clothes, 2)
	select_outfits = take_best_path_length_outfits(graph, outfit_list, combo=2) # Get best 50 outfits to score    
	sol = score_final_outfits_in_descending(select_outfits)
	return sol[:num]

