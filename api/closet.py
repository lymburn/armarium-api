from flask import jsonify
from data_access.closet_dao import closet_dao
from model.closet_model import Closet
from ml.outfit_generator import get_top_outfits
from ml.graph_manager import generate_graph, add_node_to_graph, remove_node_from_graph

def create_closet(username, closet):
    """
    This function corresponds to a POST request to /api/user/{user_name}/closet/
    with a list of all closets being returned

    :param username:      username of the user to create a closet for
    :param closet:        the closet to create
    :return:              201 on success, 409 if closet exists
    """
    try:
        closet_name = closet.get('name')
        closet = closet_dao.get_by_name(username, closet_name)

        if closet is not None:
            return "Closet with name for this user already exists", 409
        else:      
            closet_dao.create_closet(username, closet_name)
            return "Successfully created closet", 201

    except Exception as error:
        return jsonify(error = str(error)), 500

def get_closets(user_name):
    """
    This function corresponds to a GET request for /api/user/{user_name}/closet/
    with a list of all closets being returned

    :param user_name:      username of the user to retrieve from
    :return:               list of user's closets
    """
    return ''

def get_closet(username, closet_name):
    """
    This function corresponds to a GET request for /api/user/{user_name}/closet/{closet_name}
    with the specified closet being returned

    :param user_name:      username of the user to retrieve from
    :param closet_name:    name of the closet to retrieve
    :return:               (200) the user's closet matching with the name, (404) closet not found
    """

    try:
        closet = closet_dao.get_by_name(username, closet_name)
        
        if closet is not None:
            return jsonify(id = closet.closet_id,
                           name = closet.closet_name)
        else:
            return 'Closet Not Found', 404
    except Exception as error:
        return jsonify(error = str(error)), 500

# TODO: def recommend_outfits(...):
'''

'''
# TODO: make outfit_images an input instead of hardcode
# TODO: move get_best_outfit to closet_dao
def get_best_outfit():
    try:
        # hardcode the clothes dictionary for now, will retrieve from s3 and process in the future
        # this is a dictionary with the list of item names used to create nodes in the graph
        clothes = {'tops':['test-outfit/top.jpg'],
        'bottoms':['test-outfit/bottom.jpg'],
        'shoes': ['test-outfit/shoes.jpg'],
        'bags': ['test-outfit/bag.jpg'],
        'accessories':['test-outfit/accessory.jpg']}

        # TODO: change this to fetch closet graph instead of creating
        graph = create_closet_graph()
        
        score_returned = get_top_outfits(graph, clothes)
        return jsonify(score = score_returned)
    except Exception as error:
        return jsonify(error = str(error)), 500

def create_closet_graph():
    # TODO: get clothings from db or pass it in instead of hardcode
    graph = generate_graph(['test-outfit/top.jpg'],['test-outfit/bottom.jpg'],['test-outfit/shoes.jpg'],['test-outfit/bag.jpg'],['test-outfit/accessory.jpg'])
    # TODO: save this graph to s3
    return graph

def get_closet_graph():
    # TODO: some s3 connection that fetches graph from db
    pass

# TODO: unsure about the input, img is assumed to be a string used as node name
# category is a string that indicates whether it is a top, bottom, shoes, bag, or accessory
def add_clothes_to_closet(image):
    # TODO: get graph from s3 
    # creating the graph for now for testing purposes
    print("reached the function!!!!")
    graph = create_closet_graph()

    # TODO: retreive the existing nodes in graph from s3
    # hardcoding the results for testing purposes
    clothes = {'tops':['test-outfit/top.jpg'],
    'bottoms':['test-outfit/bottom.jpg'],
    'shoes': ['test-outfit/shoes.jpg'],
    'bags': ['test-outfit/bag.jpg'],
    'accessories':['test-outfit/accessory.jpg']}

    returned_graph = add_node_to_graph(graph, image.get('img'), image.get('category'), clothes)
    # TODO: save the returned graph to s3

def remove_clothes_from_closet(image):
    # TODO: get graph from s3 
    # creating the graph for now for testing purposes
    graph = create_closet_graph()
    returned_graph = remove_node_from_graph(graph, image.get('img'))

    # TODO: save the returned graph to s3

