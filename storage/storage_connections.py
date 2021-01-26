# StorageConnections class to maintain connections to database and S3
import boto3
import os
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.db_orm_mapping import Base

class StorageConnections:
    def __init__(self, db_path: str, aws_s3_region: str, aws_access_key_id: str, aws_access_key: str):
        self.db_engine = create_engine('sqlite:///' + db_path)
        Session = sessionmaker(bind=self.db_engine)
        self.db_session = Session()
        Base.metadata.create_all(self.db_engine)

        self.create_credentials_and_config(aws_s3_region, aws_access_key_id, aws_access_key)
        self.s3 = boto3.resource('s3', region_name=aws_s3_region)

    def create_credentials_and_config(aws_s3_region: str, aws_access_key_id: str, aws_access_key: str):
        # AWS config / permissions files set-up
        # Assume that "/" is root directory of svr
        os.mkdir("/.aws")
        config = open("/.aws/config", "w")
        w = '[default]\nregion = ' + aws_s3_region
        config.write(w)
        config.close()

        cred = open("/.aws/credentials", "w")
        w = '[default]\naws_access_key_id = ' + aws_access_key_id + '\naws_secret_access_key = ' + aws_access_key
        cred.write(w)
        cred.close()