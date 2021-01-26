# StorageConnections class to maintain connections to database and S3
import boto3
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_orm_mapping import Base

class StorageConnections:
    def __init__(self, db_path: str):
        self.db_engine = create_engine('sqlite:///' + db_path)
        Session = sessionmaker(bind=self.db_engine)
        self.db_session = Session()
        Base.metadata.create_all(self.db_engine)

        self.s3_region = 'us-east-2'
        self.s3 = boto3.resource('s3', region_name=self.s3_region)