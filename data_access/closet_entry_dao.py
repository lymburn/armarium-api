from model.closet_entry_model import ClosetEntry
import database.db as db

class ClosetEntryDAO:
    def get_all_entries_from_closet(self, closet_id: int):
        try:
            connections = db.get_db()

            entries = db.select_all_files_from_closet(connections, closet_id)

            closet_entry_models = []

            for entry in entries:
                filename = entry['Filename']
                bucket_name = entry['BucketName']
                object_key = entry['ObjectKey']
                category = entry['Category']

                closet_entry_model = ClosetEntry(filename, bucket_name, object_key, category)
                closet_entry_models.append(closet_entry_model)

            return closet_entry_models
        except Exception as error:
            raise error

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
