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
                    deleted_items, errors = aws_s3.delete_objects(
                        bucket, object_keys)

                ret = db.delete_user(username)

        except Exception as error:
            raise error
        else:
            return ret

    def login(self, username: str, password_hash: str):
        try:
            # NOTE: Returns {'closets': [{'closet_id': #, 'closet_name': <name>, 'items': [{'img': <data>, ...}]}]}
            # NOTE: Does not return any graph files
            info_correct = db.check_user_info_correct(username, password_hash)
            account_data = []

            if info_correct:
                closets = db.query_closets_of_user(username)

                for closet in closets:
                    closet_data = {'closet_id': closet['closet_id'],
                                   'closet_name': closet['closet_name']}
                    files = db.query_all_files_from_closet(closet['closet_id'])
                    file_data = []

                    for file in files:
                        if file['category'] != 'graph':
                            img_data = aws_s3.get_image_data(
                                file['bucket_name'], file['object_key'])
                            file['base64_encoded_image'] = img_data
                            file_data.append(file)
                    
                    closet_data['items'] = file_data
                    account_data.append(closet_data)

                return {'closets': account_data}

            return None
        except Exception as error:
            raise error


user_dao = UserDAO()
