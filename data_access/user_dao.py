from model.user_model import User
import database.db as db
import storage.aws_s3 as aws_s3


class UserDAO:
    def get_by_username(self, username: str):
        try:
            user = db.query_user_info(username)

            if user:
                user_model = User(user['username'])
                return user_model
            else:
                return None
        except Exception as error:
            raise error

    def create_user(self, user_model: User, password: str):
        try:
            username = user_model.username
            password_hash = hash(password)

            db.add_user(username, password_hash)

        except Exception as error:
            raise error

    def delete_user(self, username: str):
        try:
            # NOTE: Assume only 1 bucket
            # TODO: Deal w potential errors from S3 delete
            user = db.query_user_info(username)
            ret = False
            if user:
                closets = db.query_closets_of_user(username)
                for c in closets:
                    files = db.query_all_files_from_closet(c['closet_id'])
                    object_keys = [f['object_key'] for f in files]
                    bucket = files[0]['bucket_name']
                    deleted_items, errors = aws_s3.delete_objects(bucket, object_keys)

                ret = db.delete_user(username)

        except Exception as error:
            raise error
        else:
            return ret


user_dao = UserDAO()
