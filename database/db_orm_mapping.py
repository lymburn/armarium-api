# SQLAlchemy ORM Mapping Classes
import datetime
import typing
from flask_sqlalchemy import SQLAlchemy

sqla = SQLAlchemy()

class Users(sqla.Model):
    __tablename__ = 'Users'
    username = sqla.Column('Username', sqla.Text, primary_key=True)
    password_hash = sqla.Column('PasswordHash', sqla.Text, nullable=False)

    closets = sqla.relationship("Closets", cascade="all, delete, delete-orphan")

    def __init__(self, username, password_hash) -> None:
        self.username = username
        self.password_hash = password_hash


class Closets(sqla.Model):
    __tablename__ = 'Closets'
    closet_id = sqla.Column('ClosetID', sqla.Integer, primary_key=True, autoincrement=True)
    closet_name = sqla.Column('ClosetName', sqla.Text, nullable=False)
    username = sqla.Column('Username', sqla.Text, sqla.ForeignKey(
        'Users.Username'), nullable=False)
    
    files = sqla.relationship("Files", cascade="all, delete, delete-orphan")
    recommended_outfits = sqla.relationship("RecommendedOutfits", cascade="all, delete, delete-orphan")

    def __init__(self, closet_name, username) -> None:
        self.closet_name = closet_name
        self.username = username


class Files(sqla.Model):
    __tablename__ = 'Files'
    object_key = sqla.Column('ObjectKey', sqla.Text, primary_key=True)
    filename = sqla.Column('Filename', sqla.Text, nullable=False)
    description = sqla.Column('Description', sqla.Text, nullable = True)
    bucket_name = sqla.Column('BucketName', sqla.Text, nullable=False)
    category = sqla.Column('Category', sqla.Text, nullable=False)
    closet_id = sqla.Column('ClosetID', sqla.Integer, sqla.ForeignKey(
        'Closets.ClosetID'), nullable=False)

    def __init__(self, object_key, filename, description, bucket_name, category, closet_id) -> None:
        self.object_key = object_key
        self.filename = filename
        self.description = description
        self.bucket_name = bucket_name
        self.category = category
        self.closet_id = closet_id

class RecommendedOutfits(sqla.Model):
    __tablename__ = 'Recommended_Outfits'
    timestamp = sqla.Column('Timestamp', sqla.DateTime, primary_key=True)
    top = sqla.Column('Top', sqla.DateTime, nullable=True)
    bottom = sqla.Column('Bottom', sqla.DateTime, nullable=True)
    shoes = sqla.Column('Shoes', sqla.DateTime, nullable=True)
    bag = sqla.Column('Bag', sqla.DateTime, nullable=True)
    accessory = sqla.Column('Accessory', sqla.DateTime, nullable=True)
    closet_id = sqla.Column('ClosetID', sqla.Integer, sqla.ForeignKey('Closets.ClosetID'), nullable=False)

    def __init__(self, closet_id, top='', bottom='', shoes='', bag='', accessory='') -> None:
        # TODO: Find out how to autogenerate timestamp, if poss. Tried a couple things but they haven't worked so far.
        self.timestamp = datetime.datetime.utcnow()
        self.top = top
        self.bottom = bottom
        self.shoes = shoes
        self.bag = bag
        self.accessory = accessory
        self.closet_id = closet_id
