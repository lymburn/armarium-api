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

def add_tbs_edges(graph, tops, bottoms, shoes):
    tb_combos = generate_all_combos([tops, bottoms])
    tbs_combos = generate_all_combos([tb_combos, shoes]) # Format: [((tb), s),]
    tbs_relations = {tbs:list((tbs[0][0], tbs[0][1], tbs[1]) + (MEAN_BAG, MEAN_ACCESSORY)) for tbs in tbs_combos}
    returned_graph = add_edges_neg_weight(graph, {**tbs_relations})
    return returned_graph

# category is the type of image being added: could be top, bottom, shoes, bag, or accessory
# img is a string that represenets the image being added (should be unique) 
def add_node_to_graph(graph, img, category, clothes):
	# order is top+bottom -> shoes -> bag -> accessory
    returned_graph = None

    if category == "top":
        # add top+bottom and shoes edges
        returned_graph = add_tbs_edges(graph, [img], clothes['bottoms'], clothes['shoes'])
    elif category == "bottom":
        # add top+bottom and shoes edges
        returned_graph = add_tbs_edges(graph, clothes['tops'], [img], clothes['shoes'])
    elif category == "shoes":
        # add top+bottom and shoes edges
        gph = add_tbs_edges(graph, clothes['tops'], clothes['bottoms'], [img])
        # add shoes and bags edges
        sg_combos = generate_all_combos([[img], clothes['bags']])
        sg_relations = {sg:list((MEAN_TOP, MEAN_BOTTOM) + sg + (MEAN_ACCESSORY,)) for sg in sg_combos}
        returned_graph = add_edges_neg_weight(gph, {**sg_relations})

    elif category == "bag":
        # add shoes and bag edges
        gs_combos = generate_all_combos([clothes['shoes'], [img]])
        gs_relations = {gs:list((MEAN_TOP, MEAN_BOTTOM) + gs + (MEAN_ACCESSORY,)) for gs in gs_combos}
        # add bag and accessories edges
        ga_combos = generate_all_combos([[img], clothes['accessories']])
        ga_relations = {ga:list((MEAN_TOP, MEAN_BOTTOM, MEAN_SHOES) + ga) for ga in ga_combos}
        returned_graph = add_edges_neg_weight(graph, {**gs_relations, **ga_relations})

    elif category == "accessory":
        # add bags and accessory edges
        ag_combos = generate_all_combos([clothes['bags'], [img]])
        ag_relations = {ag:list((MEAN_TOP, MEAN_BOTTOM, MEAN_SHOES) + ag) for ag in ag_combos}
        returned_graph = add_edges_neg_weight(graph, {**ag_relations})

    else:
        print("invalid category")

    return returned_graph

# img is the name of the img that was used to add the node to the graph
# img should be a unique name
def remove_node_from_graph(graph, img):
    graph.remove_node(img)
    return graph
