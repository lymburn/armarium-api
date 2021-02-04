"""
Final chosen outfit generation algorithm

- Graph structure:
    - Edge weights = negative of score output from ML model
    - To offset biased effects of pairwise scores, we combined some categories before building the sequentially-connected, directed graph
    - Graph is currently organized as follows: (top+bottom) --> shoes --> bag --> accessory
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

# path to mean images
MEAN_TOP = "ml/upper.png"
MEAN_BOTTOM = "ml/bottom.png"
MEAN_SHOES = "ml/shoe.png"
MEAN_BAG = "ml/bag.png"
MEAN_ACCESSORY = "ml/accessory.png"

# Graph generation helper functions
def generate_all_combos(ls):
    # ls = [[], [], ...]
    # https://stackoverflow.com/questions/798854/all-combinations-of-a-list-of-lists
    output = list(itertools.product(*ls))
    return output

def add_edges_neg_weight(it_graph, relations):
    # given {(categA, categB):[outfit], ...}, add_edge(categA, categB, weight = score(outfit))
    for k, v in relations.items():
        it_graph.add_edge(k[0], k[1], weight=-1*get_outfit_score(v))
    return it_graph

def generate_graph_edges(top_imgs, bottom_imgs, shoes_imgs, bag_imgs, accessory_imgs):
    # Requireed outfit seq = tbsga
    tb_combos = generate_all_combos([top_imgs, bottom_imgs])
    tbs_combos = generate_all_combos([tb_combos, shoes_imgs]) # Format: [((tb), s),]
    tbs_relations = {tbs:list((tbs[0][0], tbs[0][1], tbs[1]) + (MEAN_BAG, MEAN_ACCESSORY)) for tbs in tbs_combos}

    sg_combos = generate_all_combos([shoes_imgs, bag_imgs])
    sg_relations = {sg:list((MEAN_TOP, MEAN_BOTTOM) + sg + (MEAN_ACCESSORY,)) for sg in sg_combos}

    ga_combos = generate_all_combos([bag_imgs, accessory_imgs])
    ga_relations = {ga:list((MEAN_TOP, MEAN_BOTTOM, MEAN_SHOES) + ga) for ga in ga_combos}

    return {**tbs_relations, **sg_relations, **ga_relations}

# Graph generation
def generate_graph(top_imgs, bottom_imgs, shoes_imgs, bag_imgs, accessory_imgs):
    # (tb) --> s --> g --> a
    tik = time.perf_counter()

    it_graph = nx.DiGraph()
    all_edges = generate_graph_edges(top_imgs, bottom_imgs, shoes_imgs, bag_imgs, accessory_imgs)
    item_graph = add_edges_neg_weight(it_graph, all_edges)

    tok = time.perf_counter()
    print(f"Graph generation took {tok-tik:0.4f} seconds")
    return item_graph

# Path search
def bellman_ford_search_best_path_len(graph, combo_imgs_one, combo_imgs_two, last_imgs, num):
    tik = time.perf_counter()
    srcs = generate_all_combos([combo_imgs_one, combo_imgs_two])
    targets = last_imgs

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

    # Repeatedly search, restoring graph aft searching a source
    valid_outfits = []
    for s in srcs:
        deleted_edges = []
        if len(srcs) == 2:
            num = 1
        for _ in itertools.repeat(None, num):
            # Given a src, find best outfit, rmv edges, repeat num times
            s_best = find_best_path(s) # Output: (score, [outfit items])
            valid_outfits.append(s_best)
            if len(srcs) < 2:
                break
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

def get_top_outfits(top_imgs, bottom_imgs, shoes_imgs, bag_imgs, accessory_imgs, num=5):
	Gsc2 = generate_graph(top_imgs, bottom_imgs, shoes_imgs, bag_imgs, accessory_imgs)   
	outfit_list = bellman_ford_search_best_path_len(Gsc2, top_imgs, bottom_imgs, accessory_imgs, 2)
	select_outfits = take_best_path_length_outfits(Gsc2, outfit_list, combo=2) # Get best 50 outfits to score    
	sol = score_final_outfits_in_descending(select_outfits)
	return sol[:num]

