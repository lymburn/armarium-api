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
        # Get file data. Bucket + key info will be added in DAO
        base64_encoded_image = closet_entry.get("base64_encoded_image")
        description = closet_entry.get("description")
        category = closet_entry.get("category")

        closet_entry_model = ClosetEntry(
            base64_encoded_image, '', description, '', '', category)

        allowed = closet_entry_dao.check_closet_size(closet_id, category)
        if not allowed:
            return "Too many items in this category", 400
        
        file_info = closet_entry_dao.create_closet_entry(
            closet_id, closet_entry_model)
        return jsonify(closet_entry=file_info), 201

    except Exception as error:
        return jsonify(error=str(error)), 500


def get_closet_entries_by_closet(closet_id):
    """
    This function corresponds to a GET request for /api/closet/{closet-id}/closet-entry
    with a list of all closet entries in that closet being returned

    :param closet_id:      id of the closet to retrieve from
    :return:               (200) list of closet entries
    """

    try:
        closet_entries = closet_entry_dao.get_all_entries_from_closet(
            closet_id)

        json_entries = []

        for entry in closet_entries:
            json_entry = {"base64_encoded_image": entry.base64_encoded_image,
                          "filename": entry.filename,
                          "description": entry.description,
                          "bucket_name": entry.bucket_name,
                          "object_key": entry.object_key,
                          "category": entry.category}

            json_entries.append(json_entry)

        return jsonify(closet_entries=json_entries), 200

    except Exception as error:
        return jsonify(error=str(error)), 500


def delete_closet_entry(closet_id, closet_entry):
    """
    This function corresponds to a DELETE request for /api/closet/{closet-id}/closet-entry/{closet-entry}

    :param closet_id:      id of the closet to delete from
    :param closet_entry:   filename of closet entry to delete
    :return:                201 on success, 404 if entry with object key does not exist
    """
    try:
        exist = closet_entry_dao.does_filename_exists_in_closet(
            closet_id, closet_entry)

        if exist:
            closet_entry_dao.delete_closet_entry(closet_id, closet_entry)
            return "Successfully deleted closet entry", 201
        else:
            return "File not found", 404

    except Exception as error:
        return jsonify(error=str(error)), 500
