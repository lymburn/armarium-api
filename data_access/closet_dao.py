from model.closet_model import Closet
import database.db as db

class ClosetDAO:
    def get_by_name(self, username: str, closet_name: str):
        try:
            connections = db.get_db()
            condition_columns = ['ClosetName']
            condition_values = [closet_name]

            closets = db.select_entry_from_table(connections, 'Closets', condition_columns, condition_values)

            if len(closets) > 0:
                closet = closets[0]
                closet_model = Closet(closet['ClosetID'], closet['ClosetName'])

                return closet_model
            else:
                return None
        except Exception as error:
            raise error

    def create_closet(self, username: str, closet_model: Closet):
        try:
            connections = db.get_db()

            closet_name = closet_model.closet_name
            columns = ['Username', 'ClosetName']
            values = [username, closet_name]

            db.insert_entry(connections, 'Closets', columns, values)

        except Exception as error:
            raise error

closet_dao = ClosetDAO()
