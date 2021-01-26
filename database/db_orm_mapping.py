# SQLAlchemy ORM Mapping Classes
import datetime
import typing
import sqlalchemy
from sqlalchemy import Column, Integer, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.schema import ForeignKey

Base = declarative_base()

class Users(Base):
    __tablename__ = 'Users'
    username = Column('Username', Text, primary_key=True)
    password_hash = Column('PasswordHash', Text, nullable=False)

    closets = relationship("Closets", cascade="all, delete, delete-orphan")

    def __init__(self, username, password_hash) -> None:
        self.username = username
        self.password_hash = password_hash


class Closets(Base):
    __tablename__ = 'Closets'
    closet_id = Column('ClosetID', Integer, primary_key=True, autoincrement=True)
    closet_name = Column('ClosetName', Text, nullable=False)
    username = Column('Username', Text, ForeignKey(
        'Users.Username'), nullable=False)
    
    files = relationship("Files", cascade="all, delete, delete-orphan")
    recommended_outfits = relationship("RecommendedOutfits", cascade="all, delete, delete-orphan")

    def __init__(self, closet_name, username) -> None:
        self.closet_name = closet_name
        self.username = username


class Files(Base):
    __tablename__ = 'Files'
    object_key = Column('ObjectKey', Text, primary_key=True)
    filename = Column('Filename', Text, nullable=False)
    bucket_name = Column('BucketName', Text, nullable=False)
    category = Column('Category', Text, nullable=False)
    closet_id = Column('ClosetID', Integer, ForeignKey(
        'Closets.ClosetID'), nullable=False)

    def __init__(self, object_key, filename, bucket_name, category, closet_id) -> None:
        self.object_key = object_key
        self.filename = filename
        self.bucket_name = bucket_name
        self.category = category
        self.closet_id = closet_id

class RecommendedOutfits(Base):
    __tablename__ = 'Recommended_Outfits'
    timestamp = Column('Timestamp', DateTime, primary_key=True)
    outfit = Column('Outfit', Text, nullable=False)
    closet_id = Column('ClosetID', Integer, ForeignKey('Closets.ClosetID'), nullable=False)

    def __init__(self, outfit, closet_id) -> None:
        # TODO: Find out how to autogenerate timestamp, if poss. Tried a couple things but they haven't worked so far.
        self.timestamp = datetime.datetime.utcnow()
        self.outfit = outfit
        self.closet_id = closet_id
