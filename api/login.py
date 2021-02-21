from flask import jsonify
from data_access.user_dao import user_dao
from model.user_model import User

def login(user):
    """
    This function corresponds to a POST request to /api/login

    :param user:    The info of the user to authenticate
    :return:        201 on success, 404 if user exists
    """
    try:
        username = user.get('username')
        password = user.get('password')

        # TODO:
        res = user_dao.login(username, hash(password))
        if res:
            return jsonify(account_data = res), 201
        else:
            return "User not found", 404

    except Exception as error:
        return jsonify(error = str(error)), 500