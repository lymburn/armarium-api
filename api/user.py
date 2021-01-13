from flask import jsonify
import database.db as db
from data_access.user_dao import user_dao
from model.user_model import User

def create_user(user):
    """
    This function corresponds to a POST request to /api/user/

    :param user:    The info of the user to create 
    :return:        201 on success, 409 if user exists
    """
    try:
        username = user.get('username')
        password = user.get('password')

        # Check if users exist
        if user_dao.get_by_username(username) is None:
            user_model = User(username)

            user_dao.create_user(user_model, password)

            return "Successfully created user", 201
        else:
            return "User already exists", 409

    except Exception as error:
        return jsonify(error = str(error)), 500
    

def get_user_by_username(username):
    """
    This function corresponds to a GET request for /api/user/{username}
    with the specified closet being returned

    :param user_name:      username of the user to retrieve
    :return:               (200) the user, (404) user not found
    """

    try:
        user = user_dao.get_by_username(username)
        
        if user is not None:
            return jsonify(username = user.username)
        else:
            return 'User Not Found', 404
    except Exception as error:
        return jsonify(error = str(error)), 500
        
    
    



