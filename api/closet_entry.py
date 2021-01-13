from flask import jsonify, make_response
import json as json
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

def get_closet_entries_by_closet(closet_id):
    """
    This function corresponds to a GET request for /api/closet/id/closet-entry
    with a list of all closet entries in that closet being returned

    :param closet_id:      id of the closet to retrieve from
    :return:               (200) list of closet entries
    """

    try:
        closet_entries = closet_entry_dao.get_all_entries_from_closet(closet_id)
        
        json_entries = []

        for entry in closet_entries:
            json_entry = {"filename": entry.filename,
                          "bucket_name": entry.bucket_name,
                          "object_key": entry.object_key,
                          "category": entry.category}

            json_entries.append(json_entry)

        return jsonify(json_entries), 200
    
    except Exception as error:
        return jsonify(error = str(error)), 500