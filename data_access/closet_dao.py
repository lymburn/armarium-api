import networkx as nx
from model.closet_model import Closet
import database.db as db
import storage.aws_s3 as aws_s3
from ml.outfit_generator import get_top_outfits
from ml.graph_manager import generate_empty_graph


class ClosetDAO:
    def get_by_name(self, username: str, closet_name: str):
        try:
            closets = db.query_closet_id(username, closet_name)

            if len(closets) > 0:
                closet = closets[0]
                closet_model = Closet(
                    closet['closet_id'], closet['closet_name'])

                return closet_model
            else:
                return None
        except Exception as error:
            raise error

    def create_closet(self, username: str, closet_name: str):
        try:
            db.add_closet(closet_name, username)
            self.create_closet_graph(username, closet_name)
        except Exception as error:
            raise error

    def create_closet_graph(self, username: str, closet_name: str):
        try:
            graph = generate_empty_graph()
            buckets = aws_s3.get_buckets()
            bucket_name = buckets[0]
            object_key = aws_s3.create_object_key(closet_name)
            closet_ids = db.query_closet_id(username, closet_name)
            db.add_file(object_key, closet_name, '',
                        bucket_name, 'graph', closet_ids[0]['closet_id'])
            aws_s3.upload_graph(graph, bucket_name, object_key)
            return graph
        except Exception as error:
            raise error

    def delete_closet(self, closet_model: Closet):
        # Assuming only 1 AWS bucket
        try:
            closet_files = db.query_all_files_from_closet(
                closet_model.closet_id)
            if len(closet_files) > 0:
                bucket = closet_files[0]['bucket_name']
                keys = [f['object_key'] for f in closet_files]
                aws_s3.delete_objects(bucket, keys)
            db.delete_closet(closet_model.closet_id)
        except Exception as error:
            raise error

    def recommend_outfit(self, closet_id: int):
        # Fetch graph from S3 + create ML algorithm inputs
        files = db.query_all_files_from_closet_grouped_by_category(closet_id)
        clothes = {'top': [f['object_key'] for f in files['top']],
                   'bottom': [f['object_key'] for f in files['bottom']],
                   'shoes': [f['object_key'] for f in files['shoes']],
                   'bag': [f['object_key'] for f in files['bag']],
                   'accessory': [f['object_key'] for f in files['accessory']]}

        g_info = db.query_graph_key(closet_id)
        graph = aws_s3.get_graph(g_info['bucket_name'], g_info['object_key'])

        # NOTE: Can specify # of returned outfits, default 5 or less
        outfits = get_top_outfits(graph, clothes)
        # TODO: Edit function to change output to smth like [[outfit obj key nodes]]
        
        # TODO: do smth w recommendedOutfits + return top oufit CHECK that RecOutfit holds obj keys + not filenames
        outfit = .... (from above), list of keys
        # TODO: Return outfit data
        for out in outfit:
            aws_s3.get_file()  # return json obj of byte strs

        pass


closet_dao = ClosetDAO()
