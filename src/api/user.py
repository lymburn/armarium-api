from flask import abort, make_response
import database.db as db

CLOSET = {
    "eugene": {
        "yll": {
            "filename": "2.jpg",
            "object_key": "bbb",
            "category": "bottom"
        }
    }
}

def create_closet(user_name, closet_name):
    """
    This function corresponds to a POST request to /api/user/{user_name}/closet/
    with a list of all closets being returned

    :param user_name:      username of the user to create a closet for
    :param closet_name:    username of the user to create a closet for
    :return:               201 on success, 409 if closet exists
    """

    connections = db.get_db()

    # TODO: Check if closet already exists
    db.create_table(connections, user_name, closet_name)

    return make_response(201)

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

    if user_name in CLOSET:
        user = CLOSET.get(user_name)

        if closet_name in user:
            closet = user.get(closet_name)

    else:
        return make_response("Closet with name {closet_name} not found".format(closet_name=closet_name), 404)

    return make_response(closet, 200)