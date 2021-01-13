from model.user_model import User
import database.db as db

class UserDAO:
    def get_by_username(self, username: str):
        try:
            connections = db.get_db()
            users = db.select_entry_from_table(connections, 'Users', ['Username'], [username])
            
            if len(users) > 0:
                user = users[0]
                user_model = User(user['username'])
                return user_model
            else:
                return None
        except Exception as error:
            raise error

    def create_user(self, user_model: User, password: str):
        try:
            connections = db.get_db()

            username = user_model.username
            password_hash = hash(password)
            columns = ['Username', 'PasswordHash']
            values = [username, password_hash]

            db.insert_entry(connections, 'Users', columns, values)

        except Exception as error:
            raise error

user_dao = UserDAO()
