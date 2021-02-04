from model.user_model import User
import database.db as db

class UserDAO:
    def get_by_username(self, username: str):
        try:
            user = db.query_user_info(username)
            
            if user:
                user_model = User(user['username'])
                return user_model
            else:
                return None
        except Exception as error:
            raise error

    def create_user(self, user_model: User, password: str):
        try:
            username = user_model.username
            password_hash = hash(password)

            db.add_user(username, password_hash)

        except Exception as error:
            raise error

user_dao = UserDAO()
