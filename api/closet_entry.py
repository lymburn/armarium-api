from flask import make_response
import database.db as db
from model.closet_entry_model import ClosetEntry

def create_closet_entry(user_name, closet_name, closet_entry):
    """
    This function corresponds to a POST request to /api/user/{user_name}/closet/{closet_name}/entry
    with a list of all closets being returned

    :param user_name:      username of the user's closet to add entries to
    :param closet_name:    the name of the closet to add entries to
    :return:               201 on success
    """

    connections = db.get_db()

    filename = closet_entry.get("filename")
    object_key = closet_entry.get("object_key")
    category = closet_entry.get("category")

    entry = ClosetEntry(filename, object_key, category)

    db.add_entry(connections, user_name, closet_name, entry)

    return make_response("Successfully created closet entry", 201)