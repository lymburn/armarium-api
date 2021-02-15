from flask import jsonify, make_response
import json as json
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
        # Get file data, bucket + key info will be added in DAO
        base64_encoded_image = closet_entry.get("base64_encoded_image")
        filename = closet_entry.get("filename")
        description = closet_entry.get("description")
        category = closet_entry.get("category")

        exist = closet_entry_dao.does_filename_exists_in_closet(closet_id, filename)
    
        if exist:
            return "File with this filename for this closet already exists", 409
        else:
            closet_entry_model = ClosetEntry(base64_encoded_image, filename, description, '', '', category)
            closet_entry_dao.create_closet_entry(closet_id, closet_entry_model)
            return "Successfully created closet entry", 201

    except Exception as error:
        return jsonify(error = str(error)), 500

def get_closet_entries_by_closet(closet_id):
    """
    This function corresponds to a GET request for /api/closet/{closet-id}/closet-entry
    with a list of all closet entries in that closet being returned

    :param closet_id:      id of the closet to retrieve from
    :return:               (200) list of closet entries
    """

    try:
        closet_entries = closet_entry_dao.get_all_entries_from_closet(closet_id)
        
        json_entries = []

        for entry in closet_entries:
            json_entry = {"base64_encoded_image": entry.base64_encoded_image,
                          "filename": entry.filename,
                          "description": entry.description,
                          "bucket_name": entry.bucket_name,
                          "object_key": entry.object_key,
                          "category": entry.category}

            json_entries.append(json_entry)

        return jsonify(json_entries), 200
    
    except Exception as error:
        return jsonify(error = str(error)), 500


def delete_closet_entry(closet_id, filename):
    # TODO: call DAO delete_closet_entry
    # New path needed: /closet/{closet-id}/closet-entry/{filename}
    pass