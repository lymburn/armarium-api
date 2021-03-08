import base64
from networkx.generators.intersection import general_random_intersection_graph
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import io
import random
import time
import os
import json
import sys
import torch
import torchvision.transforms as transforms
import re
import operator
import networkx as nx
import logging
import itertools
from collections import deque
from matplotlib import rcParams
from PIL import Image
import ml.graph_manager as gm
from ml.outfit_generator import get_top_outfits

def generate_incomplete_graph_edges(incomplete_outfit):
    # Requireed outfit seq = tbsga
        
    tb_combos = gm.generate_all_combos([incomplete_outfit["top"], incomplete_outfit["bottom"]])
    
    tbs_combos = gm.generate_all_combos([tb_combos, incomplete_outfit["shoe"]]) # Format: [((tb), s),]
    tbs_relations = {tbs:list((tbs[0][0], tbs[0][1], tbs[1]) + (gm.MEAN_BAG, gm.MEAN_ACCESSORY)) for tbs in tbs_combos}

    sg_combos = gm.generate_all_combos([incomplete_outfit["shoe"], incomplete_outfit["bag"]])
    sg_relations = {sg:list((gm.MEAN_TOP, gm.MEAN_BOTTOM) + sg + (gm.MEAN_ACCESSORY,)) for sg in sg_combos}

    ga_combos = gm.generate_all_combos([incomplete_outfit["bag"], incomplete_outfit["accessory"]])
    ga_relations = {ga:list((gm.MEAN_TOP, gm.MEAN_BOTTOM, gm.MEAN_SHOES) + ga) for ga in ga_combos}

    return {**tbs_relations, **sg_relations, **ga_relations}


def generate_incomplete_graph(og_graph, incomplete_outfit):
    # (tb) --> s --> g --> a
    # tik = time.perf_counter()

    it_graph = nx.DiGraph()
    all_edges = generate_incomplete_graph_edges(incomplete_outfit)
    # TODO: orig_graph.get_edge_data(u,v) to get edge weights for subgraph, equiv to G[u][v]["weight"]
    for k, v in all_edges:
        weight = og_graph[k[0]][k[1]]['weight']
        it_graph.add_edge(k[0], k[1], weight=-1*weight)
        # all_edges[k] = weight

    # item_graph = gm.add_edges_neg_weight(it_graph, all_edges)

    # tok = time.perf_counter()
    # print(f"Semicombined (2 categories combined) directed graph generation took {tok-tik:0.4f} seconds")
    return it_graph


def wrapper(og_graph, incomplete_outfit):
    graph = generate_incomplete_graph(og_graph, incomplete_outfit)
    outfit = get_top_outfits(graph, incomplete_outfit, num=1)
    return outfit