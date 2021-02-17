from model.closet_model import Closet
import database.db as db
import storage.aws_s3 as aws_s3

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
    
    # TODO: def get_best_outfit():
    '''
    Call algorithms from ML
    (maybe call to S3 to get img data to return back if ness)
    '''

    def delete_closet(self, closet_model: Closet):
        # Assuming only 1 AWS bucket
        try:
            closet_files = db.query_all_files_from_closet(closet_model.closet_id)
            if len(closet_files) > 0:
                bucket = closet_files[0]['bucket_name']
                keys = [f['object_key'] for f in closet_files]
                aws_s3.delete_objects(bucket, keys)
            db.delete_closet(closet_model.closet_id)
        except Exception as error:
            raise error

closet_dao = ClosetDAO()
