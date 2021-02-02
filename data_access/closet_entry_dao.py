from model.closet_entry_model import ClosetEntry
import database.db as db
import storage.aws_s3 as aws_s3
import base64
import io

class ClosetEntryDAO:
    def get_all_entries_from_closet(self, closet_id: int):
        try:
            entries = db.query_all_files_from_closet(closet_id)

            closet_entry_models = []

            for entry in entries:
                filename = entry['filename']
                bucket_name = entry['bucket_name']
                object_key = entry['object_key']
                category = entry['category']
                base64_encoded_image = self.get_image_by_object_key(bucket_name, object_key)

                closet_entry_model = ClosetEntry(base64_encoded_image ,filename, bucket_name, object_key, category)
                closet_entry_models.append(closet_entry_model)

            return closet_entry_models
        except Exception as error:
            raise error

    def get_image_by_object_key(self, bucket_name: str, object_key: str):
        img_byte_str = aws_s3.get_image_base64_byte_str(bucket_name, object_key)
        return img_byte_str

    def create_closet_entry(self, closet_id: int, closet_entry_model: ClosetEntry):
        try:
            filename = closet_entry_model.filename
            bucket_name = closet_entry_model.bucket_name
            object_key = closet_entry_model.object_key
            category = closet_entry_model.category

            db.add_file(object_key, filename, bucket_name, category, closet_id)
            self.upload_image(bucket_name, object_key, closet_entry_model.base64_encoded_image)
        except Exception as error:
            raise error

    def upload_image(self, bucket_name: str, object_key: str, base64_encoded_image: str):
        try:
            aws_s3.upload_image(base64_encoded_image, bucket_name, object_key)
        except Exception as error:
            raise error

closet_entry_dao = ClosetEntryDAO()
