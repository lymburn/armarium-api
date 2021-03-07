from model.closet_entry_model import ClosetEntry
import database.db as db
import storage.aws_s3 as aws_s3
import base64
import io
from ml.graph_manager import add_node_to_graph, remove_node_from_graph


class ClosetEntryDAO:
    def get_all_entries_from_closet(self, closet_id: int):
        try:
            entries = db.query_all_files_from_closet(closet_id)
            closet_entry_models = []

            for entry in entries:
                if entry['category'] != 'graph':
                    filename = entry['filename']
                    description = entry['description']
                    bucket_name = entry['bucket_name']
                    object_key = entry['object_key']
                    category = entry['category']
                    base64_encoded_image = self.get_image_by_object_key(
                        bucket_name, object_key)

                    closet_entry_model = ClosetEntry(
                        base64_encoded_image, filename, description, bucket_name, object_key, category)
                    closet_entry_models.append(closet_entry_model)
            
            return closet_entry_models
        except Exception as error:
            raise error

    def get_image_by_object_key(self, bucket_name: str, object_key: str):
        img_data = aws_s3.get_image_data(bucket_name, object_key)
        return img_data

    def does_filename_exists_in_closet(self, closet_id: int, filename: str):
        try:
            files = db.query_file_key(closet_id, filename)

            if len(files) > 0:
                return True
            else:
                return False
        except Exception as error:
            raise error

    def create_closet_entry(self, closet_id: int, closet_entry_model: ClosetEntry):
        try:
            description = closet_entry_model.description
            category = closet_entry_model.category

            # Pick bucket + generate key
            buckets = aws_s3.get_buckets()
            bucket_name = buckets[0]
            filename, object_key = aws_s3.create_object_key(description)

            db.add_file(object_key, filename, description,
                        bucket_name, category, closet_id)
            self.upload_image(bucket_name, object_key,
                              closet_entry_model.base64_encoded_image)
            self.add_item_to_closet_graph(closet_id, object_key, category)

            return filename
        except Exception as error:
            raise error

    def upload_image(self, bucket_name: str, object_key: str, base64_encoded_image: str):
        try:
            aws_s3.upload_image(base64_encoded_image, bucket_name, object_key)
        except Exception as error:
            raise error

    def add_item_to_closet_graph(self, closet_id: int, image_object_key: str, category: str):
        try:
            # Fetch graph from S3 + get all file obj keys for closet
            graph_info = db.query_graph_key(closet_id)
            graph = aws_s3.get_graph(
                graph_info['bucket_name'], graph_info['object_key'])

            files = db.query_all_files_from_closet_grouped_by_category(
                closet_id)
            clothes = {'top': [f['object_key'] for f in files['top']],
                       'bottom': [f['object_key'] for f in files['bottom']],
                       'shoes': [f['object_key'] for f in files['shoes']],
                       'bag': [f['object_key'] for f in files['bag']],
                       'accessory': [f['object_key'] for f in files['accessory']]}

            # Add to graph + save new graph in S3
            returned_graph = add_node_to_graph(
                graph, image_object_key, category, clothes)
            aws_s3.upload_graph(
                returned_graph, graph_info['bucket_name'], graph_info['object_key'])

            # print(f"DEBUG: List of nodes in returned graph: {list(returned_graph.nodes)}")
        except Exception as error:
            raise error

    def delete_closet_entry(self, closet_id: int, filename: str):
        try:
            files = db.query_file_key(closet_id, filename)
            if len(files) > 0:
                self.remove_item_from_closet_graph(closet_id, filename)
                aws_s3.delete_object(
                    files[0]['bucket_name'], files[0]['object_key'])
                db.delete_all_recommended_outfits_with_file(
                    closet_id, filename)
                db.delete_file(files[0]['object_key'])
        except Exception as error:
            raise error

    def remove_item_from_closet_graph(self, closet_id: int, filename: str):
        try:
            # Get graph from S3 + file info from database
            graph_info = db.query_graph_key(closet_id)
            graph = aws_s3.get_graph(
                graph_info['bucket_name'], graph_info['object_key'])
            files = db.query_file_key(closet_id, filename)

            # Edit graph + overwrite in S3
            returned_graph = remove_node_from_graph(
                graph, files[0]['object_key'], files[0]['category'])
            aws_s3.upload_graph(
                returned_graph, graph_info['bucket_name'], graph_info['object_key'])

            # print(
            #     f"DEBUG: Remove from graph, returned graph nodes: {list(returned_graph.nodes)}")
        except Exception as error:
            raise error


closet_entry_dao = ClosetEntryDAO()
