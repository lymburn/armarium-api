"""
Generate Graph and have functions manage the graph (ex: add and delete nodes)
- Graph structure:
    - Edge weights = negative of score output from ML model
    - To offset biased effects of pairwise scores, we combined some categories before building the sequentially-connected, directed graph
    - Graph is currently organized as follows: (top+bottom) --> shoes --> bag --> accessory
"""
import time
import networkx as nx
import itertools
from ml.outfit_grader import get_outfit_score
import matplotlib.pyplot as plt

# path to mean images
MEAN_TOP = "ml/upper.png"
MEAN_BOTTOM = "ml/bottom.png"
MEAN_SHOES = "ml/shoe.png"
MEAN_BAG = "ml/bag.png"
MEAN_ACCESSORY = "ml/accessory.png"

# Graph generation helper functions
def generate_all_combos(ls):
    # ls = [[], [], ...]
    # output = [()]
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

def generate_empty_graph():
    graph = nx.DiGraph()
    return graph

# graph plotting util function
def plot_graph(graph, show_edge_weight=False):
    edges = [(u, v) for (u, v, d) in graph.edges(data=True)]
    pos = nx.spring_layout(graph)  # positions for all nodes
    # nodes
    nx.draw_networkx_nodes(graph, pos, node_size=700)
    # edges
    if show_edge_weight:
        labels = nx.get_edge_attributes(graph,'weight')
        nx.draw_networkx_edge_labels(graph,pos,edge_labels=labels)
    nx.draw_networkx_edges(graph, pos, edgelist=edges, width=2)
    # labels
    nx.draw_networkx_labels(graph, pos, font_size=20, font_family="sans-serif")

    plt.axis("off")
    plt.show()

def add_tbs_edges(graph, tops, bottoms, shoes):
    tb_combos = generate_all_combos([tops, bottoms])
    tbs_combos = generate_all_combos([tb_combos, shoes]) # Format: [((tb), s),]
    tbs_relations = {tbs:list((tbs[0][0], tbs[0][1], tbs[1]) + (MEAN_BAG, MEAN_ACCESSORY)) for tbs in tbs_combos}
    returned_graph = add_edges_neg_weight(graph, {**tbs_relations})
    return returned_graph

# category is the type of image being added: could be top, bottom, shoes, bag, or accessory
def add_node_to_graph(graph, image_object_key, category, clothes):
	# order is top+bottom -> shoes -> bag -> accessory

    if category == "top":
        # add top+bottom and shoes edges
        # if there are no nodes to its left and right, then just add a node with no edges
        if not clothes['shoes'] and clothes['bottom']:
            tb_combos = generate_all_combos([[image_object_key], clothes['bottom']])
            for c in tb_combos:
                graph.add_node(c)
        else:
            graph = add_tbs_edges(graph, [image_object_key], clothes['bottom'], clothes['shoes'])
    elif category == "bottom":
        # add top+bottom and shoes edges
        if not clothes['shoes'] and clothes['top']:
            tb_combos = generate_all_combos([clothes['top'], [image_object_key]])
            for c in tb_combos:
                graph.add_node(c)
        else:
            graph = add_tbs_edges(graph, clothes['top'], [image_object_key], clothes['shoes'])
    elif category == "shoes":

        if (not clothes['top'] or not clothes['bottom']) and not clothes['bag']:
            graph.add_node(image_object_key)
        else:
            # add top+bottom and shoes edges
            gph = add_tbs_edges(graph, clothes['top'], clothes['bottom'], [image_object_key])
            # add shoes and bags edges
            sg_combos = generate_all_combos([[image_object_key], clothes['bag']])
            sg_relations = {sg:list((MEAN_TOP, MEAN_BOTTOM) + sg + (MEAN_ACCESSORY,)) for sg in sg_combos}
            graph = add_edges_neg_weight(gph, {**sg_relations})

    elif category == "bag":

        if not clothes['shoes'] and not clothes['accessory']:
            graph.add_node(image_object_key)
        else:
            # add shoes and bag edges
            gs_combos = generate_all_combos([clothes['shoes'], [image_object_key]])
            gs_relations = {gs:list((MEAN_TOP, MEAN_BOTTOM) + gs + (MEAN_ACCESSORY,)) for gs in gs_combos}
            # add bag and accessories edges
            ga_combos = generate_all_combos([[image_object_key], clothes['accessory']])
            ga_relations = {ga:list((MEAN_TOP, MEAN_BOTTOM, MEAN_SHOES) + ga) for ga in ga_combos}
            graph = add_edges_neg_weight(graph, {**gs_relations, **ga_relations})

    elif category == "accessory":
        # add bags and accessory edges
        if not clothes['bag']:
            graph.add_node(image_object_key)
        else:
            ag_combos = generate_all_combos([clothes['bag'], [image_object_key]])
            ag_relations = {ag:list((MEAN_TOP, MEAN_BOTTOM, MEAN_SHOES) + ag) for ag in ag_combos}
            graph = add_edges_neg_weight(graph, {**ag_relations})
    else:
        print("Error: invalid category")

    return graph

# img is the name of the img that was used to add the node to the graph
# img should be a unique name
def remove_node_from_graph(graph, img, category):

    # this is the case when the node name is combined
    if category == "top" or category == "bottom":
        nodes = list(graph.nodes)
        del_nodes = [k for k in nodes if img in k]
        graph.remove_nodes_from(del_nodes)
    else:
        graph.remove_node(img)
    return graph

