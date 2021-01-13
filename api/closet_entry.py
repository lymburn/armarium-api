from flask import jsonify
import database.db as db
from model.closet_entry_model import ClosetEntry
from data_access.closet_entry_dao import closet_entry_dao

def create_closet_entry(closet_id, closet_entry):
    """
    This function corresponds to a POST request to /api/closet/{closet_id}/closet-entry
    with a list of all closets being returned

    :param closet_id:       id of the closet to add entry to
    :param closet_entry:    the name of the closet to add entries to
    :return:                201 on success, 409 if entry with object key already exists
    """

    try:
        filename = closet_entry.get("filename")
        bucket_name = closet_entry.get("bucket_name")
        object_key = closet_entry.get("object_key")
        category = closet_entry.get("category")

        closet_entry_model = ClosetEntry(filename, bucket_name, object_key, category)

        closet_entry_dao.create_closet_entry(closet_id, closet_entry_model)

        return "Successfully created closet entry", 201

    except Exception as error:
        return jsonify(error = str(error)), 500


