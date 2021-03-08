import networkx as nx
from torch import allclose
import ml.graph_manager as gm
from ml.outfit_generator import get_top_outfits


def generate_subgraph_edges(filtered_outfit_items):
    # Get list containing all pairs of nodes we wish to connect with an edge
    # Return [(node1, node2)], where we want an edge connecting node1 to node2
    all_combos = []
    tb_combos = gm.generate_all_combos(
        [filtered_outfit_items['top'], filtered_outfit_items['bottom']])
    tbs_combos = gm.generate_all_combos(
        [tb_combos, filtered_outfit_items['shoes']])  # Expect: [((tb), s)]
    all_combos += tbs_combos

    sg_combos = gm.generate_all_combos(
        [filtered_outfit_items['shoes'], filtered_outfit_items['bag']])
    all_combos += sg_combos

    ga_combos = gm.generate_all_combos(
        [filtered_outfit_items['bag'], filtered_outfit_items['accessory']])
    all_combos += ga_combos

    return all_combos


def generate_subgraph(original_graph, filtered_outfit_items):
    # Graph structure: (tb) --> s --> g --> a
    it_graph = nx.DiGraph()
    all_combos = generate_subgraph_edges(filtered_outfit_items)
    
    for tup in all_combos:
        edge_weight = original_graph[tup[0]][tup[1]]["weight"]
        it_graph.add_edge(tup[0], tup[1], weight=edge_weight)

    return it_graph


def get_complete_the_look_outfit(original_graph, filtered_outfit_items):
    subgraph = generate_subgraph(original_graph, filtered_outfit_items)
    outfit = get_top_outfits(subgraph, filtered_outfit_items, num=1)
    return outfit
