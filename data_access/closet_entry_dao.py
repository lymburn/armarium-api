from model.closet_entry_model import ClosetEntry
import database.db as db
import base64

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
                base64_encoded_image = get_image_by_filename(filename)

                closet_entry_model = ClosetEntry(base64_encoded_image ,filename, bucket_name, object_key, category)
                closet_entry_models.append(closet_entry_model)

            return closet_entry_models
        except Exception as error:
            raise error

    def get_image_by_filename(filename: str):
        # TODO: Do S3 stuff
        return ""

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

            upload_image(closet_entry_model.base64_encoded_image)

        except Exception as error:
            raise error

    def upload_image(self, base64_encoded_image: str):
        try:
            image_bytes = base64.b64decode(base64_encoded_image)

            # TODO: Do stuff with s3

        except Exception as error:
            raise error

closet_entry_dao = ClosetEntryDAO()
