from model.closet_model import Closet
import database.db as db

class ClosetDAO:
    def get_by_name(self, username: str, closet_name: str):
        try:
            closets = db.query_closet_id(username, closet_name)

            if len(closets) > 0:
                closet = closets[0]
                closet_model = Closet(closet['closet_id'], closet['closet_name'])

                return closet_model
            else:
                return None
        except Exception as error:
            raise error

    def create_closet(self, username: str, closet_name: str):
        try:
            closet_id = db.add_closet(closet_name, username)
        except Exception as error:
            raise error
        else:
            return closet_id

    def delete_closet(self, username: str, closet_name: str):
        # TODO: get closet id, get all files in closet, delete all files in s3, delete closet in DB
        pass

closet_dao = ClosetDAO()
