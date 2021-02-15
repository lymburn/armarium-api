from model.closet_entry_model import ClosetEntry
import networkx as nx
from networkx.readwrite import json_graph
from collections import defaultdict
import typing
from typing import Any, List, Set, Dict, Tuple, Optional, BinaryIO, DefaultDict
import networkx as nx
from networkx.readwrite import json_graph
import json
import uuid
import base64
import os
import io
from database.db_orm_mapping import sqla, Users, Closets, Files, RecommendedOutfits

# TODO: Edit File functions to return description
# TODO: Add try-except to catch SQLAlchemy errors

# Database access functions
def add_user(username: str, password_hash: str) -> None:
    usr = Users(username, password_hash)
    add_persist(usr)


def add_closet(closet_name: str, username: str) -> None:
    closet = Closets(closet_name, username)
    add_persist(closet)


def add_file(object_key: str, filename: str, description: str, bucket_name: str, category: str, closet_id: int) -> None:
    file = Files(object_key, filename, description, bucket_name, category, closet_id)
    add_persist(file)


def add_recommended_outfit(outfit: List[str], closet_id: int) -> None:
    outfit_str = ','.join(outfit)
    rec_outfit = RecommendedOutfits(outfit_str, closet_id)
    add_persist(rec_outfit)


def add_persist(obj: Any) -> None:
    # Helper func
    sqla.session.add(obj)
    sqla.session.commit()


def delete_user(username: str) -> bool:
    usr = sqla.session.query(Users).filter(
        Users.username == username).all()
    if usr:
        delete_persist(usr[0])
        return True
    else:
        return False


def delete_closet(closet_id: int) -> bool:
    closet = closet = sqla.session.query(Closets).filter(
        Closets.closet_id == closet_id).all()
    if closet:
        delete_persist(closet[0])
        return True
    else:
        return False


def delete_file(object_key: str) -> bool:
    file = sqla.session.query(Files).filter(
        Files.object_key == object_key).all()
    if file:
        delete_persist(file[0])
        return True
    else:
        return False


def delete_all_files_in_closet(closet_id: int) -> bool:
    files = sqla.session.query(Files).filter(
        Files.closet_id == closet_id).all()
    if files:
        for f in files:
            delete_persist(f)
        return True
    else:
        return False


def delete_all_files_in_closet_category(closet_id: int, category: str) -> bool:
    files = sqla.session.query(Files).filter(
        Files.closet_id == closet_id, Files.category == category).all()
    if files:
        for f in files:
            delete_persist(f)
        return True
    else:
        return False


def delete_all_closet_recommended_outfits():
    # TODO:
    pass

def delete_persist(obj: Any) -> None:
    # Helper func
    sqla.session.delete(obj)
    sqla.session.commit()


def query_user_info(username: str) -> Dict:
    usr = sqla.session.query(Users).filter(
        Users.username == username).all()
    res = {}
    if usr:
        res = {'username': usr[0].username,
               'password_hash': usr[0].password_hash}
    return res


def query_closet_info(closet_id: int) -> Dict:
    closet = sqla.session.query(Closets).filter(
        Closets.closet_id == closet_id).all()
    res = {}
    if closet:
        res = {'closet_id': closet[0].closet_id, 'closet_name': closet[0].closet_name,
               'username': closet[0].username}
    return res


def query_closet_id(username: str, closet_name: str) -> List:
    # Returns list since a user may have multiple closets with the same name
    closets = sqla.session.query(Closets).filter(
        Closets.username == username, Closets.closet_name == closet_name).all()
    res = []
    if closets:
        res = [{'closet_id': c.closet_id, 'closet_name': c.closet_name,
                'username': c.username} for c in closets]
    return res


def query_closets_of_user(username: str) -> List:
    closets = sqla.session.query(Closets).filter(
        Closets.username == username).all()
    res = []
    if closets:
        res = [{'closet_id': c.closet_id, 'closet_name': c.closet_name}
               for c in closets]
    return res


def query_all_files_from_closet(closet_id: int) -> List:
    files = sqla.session.query(Files).filter(
        Files.closet_id == closet_id).all()
    res = []
    if files:
        res = [{'filename': f.filename, 'description': f.description, 'object_key': f.object_key, 'bucket_name': f.bucket_name,
                'category': f.category, 'closet_id': f.closet_id} for f in files]

    return res


def query_all_files_from_closet_grouped_by_category(closet_id: int) -> DefaultDict:
    files = sqla.session.query(Files).filter(
        Files.closet_id == closet_id).all()
    res = defaultdict(list)
    if files:
        for f in files:
            res[f.category].append(
                {'filename': f.filename, 'object_key': f.object_key, 'bucket_name': f.bucket_name})
    return res


def query_all_files_from_closet_category(closet_id: int, category: str) -> List:
    files = sqla.session.query(Files).filter(
        Files.closet_id == closet_id, Files.category == category).all()
    res = []
    if files:
        res = [{'filename': f.filename, 'object_key': f.object_key,
                'bucket_name': f.bucket_name} for f in files]
    return res


def query_file_info(object_key: str) -> Dict:
    file = sqla.session.query(Files).filter(
        Files.object_key == object_key).all()
    res = {}
    if file:
        res = {'filename': file[0].filename, 'bucket_name': file[0].bucket_name,
               'category': file[0].category, 'closet_id': file[0].closet_id}
    return res


def query_file_key(closet_id: int, filename: str) -> List:
    # Returns list since a closet may have multiple files with the same name
    files = sqla.session.query(Files).filter(
        Files.filename == filename, Files.closet_id == closet_id).all()
    res = []
    if files:
        res = [{'object_key': f.object_key, 'bucket_name': f.bucket_name,
                'category': f.category} for f in files]
    return res
