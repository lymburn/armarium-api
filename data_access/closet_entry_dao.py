from model.closet_entry_model import ClosetEntry
import database.db as db

class ClosetEntryDAO:
    # def get_by_name(self, username: str, closet_name: str):
    #     try:
    #         connections = db.get_db()
    #         condition_columns = ['ClosetName']
    #         condition_values = [closet_name]

    #         closets = db.select_entry_from_table(connections, 'Closets', condition_columns, condition_values)

    #         if len(closets) > 0:
    #             closet = closets[0]
    #             closet_model = Closet(closet['ClosetID'], closet['ClosetName'])

    #             return closet_model
    #         else:
    #             return None
    #     except Exception as error:
    #         raise error

    def create_closet_entry(self, closet_id: int, closet_entry_model: ClosetEntry):
        try:
            connections = db.get_db()

            filename = closet_entry_model.filename
            bucket_name = closet_entry_model.bucket_name
            object_key = closet_entry_model.object_key
            category = closet_entry_model.category

            columns = ['Filename', 'BucketName', 'ObjectKey', 'Category', 'ClosetId']
            values = [filename, bucket_name, object_key, category, closet_id]

            db.insert_entry(connections, 'Files', columns, values)

        except Exception as error:
            raise error

closet_entry_dao = ClosetEntryDAO()
