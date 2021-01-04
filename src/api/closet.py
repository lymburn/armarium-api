from flask import make_response
import database.db as db
from model import closet_model, closet_entry_model

def create_closet(user_name, closet):
    """
    This function corresponds to a POST request to /api/user/{user_name}/closet/
    with a list of all closets being returned

    :param user_name:      username of the user to create a closet for
    :param closet:         the closet to create
    :return:               201 on success, 409 if closet exists
    """

    # TODO: Error handling
    connections = db.get_db()

    closet_name = closet.get("name")

    # TODO: Check if closet already exists
    db.create_table(connections, user_name, closet_name)

    return make_response("Successfully created closet", 201)

def get_closets(user_name):
    """
    This function corresponds to a GET request for /api/user/{user_name}/closet/
    with a list of all closets being returned

    :param user_name:      username of the user to retrieve from
    :return:               list of user's closets
    """

def get_closet(user_name, closet_name):
    """
    This function corresponds to a GET request for /api/user/{user_name}/closet/{closet_name}
    with the specified closet being returned

    :param user_name:      username of the user to retrieve from
    :param closet_name:    name of the closet to retrieve
    :return:               (200) the user's closet matching with the name, (404) closet not found
    """

    connections = db.get_db()

    # TODO: Cleanup to be more pleasant
    closet_entries = db.select_entries_from_closet(connections, user_name, closet_name)

    return make_response("Sample", 200)