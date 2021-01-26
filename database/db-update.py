# Re-implementation of DB functions using SQLAlchemy
from collections import defaultdict
import sqlalchemy
from sqlalchemy.sql.sqltypes import Boolean
import typing
from typing import Any, List, Set, Dict, Tuple, Optional, BinaryIO, DefaultDict
import networkx as nx
from networkx.readwrite import json_graph
import json
import uuid
import base64
import os
import io
from PIL import Image
from database.db_orm_mapping import Users, Closets, Files, RecommendedOutfits
from storage.storage_connections import StorageConnections


def add_user(connections: StorageConnections, username: str, password_hash: str) -> None:
    usr = Users(username, password_hash)
    add_persist(connections, usr)


def add_closet(connections: StorageConnections, closet_name: str, username: str) -> None:
    closet = Closets(closet_name, username)
    add_persist(connections, closet)


def add_file(connections: StorageConnections, object_key: str, filename: str, bucket_name: str, category: str, closet_id: int) -> None:
    file = Files(object_key, filename, bucket_name, category, closet_id)
    add_persist(connections, file)


def add_recommended_outfit(connections: StorageConnections, outfit: List[str], closet_id: int) -> None:
    outfit_str = ','.join(outfit)
    rec_outfit = RecommendedOutfits(outfit_str, closet_id)
    add_persist(connections, rec_outfit)


def add_persist(connections: StorageConnections, obj: Any) -> None:
    # Helper func
    connections.db_session.add(obj)
    connections.db_session.commit()


def delete_user(connections: StorageConnections, username: str) -> None:
    # TODO: Should cascade delete all closets assoc w user + files assoc w closets
    usr = connections.db_session.query(Users).filter(
        Users.username == username).all()
    delete_persist(connections, usr[0])


def delete_closet(connections: StorageConnections, closet_id: int) -> None:
    # TODO: Should cascade delete all files in closet
    closet = closet = connections.db_session.query(Closets).filter(
        Closets.closet_id == closet_id).all()
    delete_persist(connections, closet[0])


def delete_file(connections: StorageConnections, object_key: str) -> None:
    file = connections.db_session.query(Files).filter(
        Files.object_key == object_key).all()
    delete_persist(connections, file[0])


def delete_all_files_in_closet(connections: StorageConnections, closet_id: int) -> None:
    files = connections.db_session.query(Files).filter(
        Files.closet_id == closet_id).all()
    for f in files:
        delete_persist(connections, f)

def delete_all_files_in_closet_category(connections: StorageConnections, closet_id: int, category: str) -> None:
    files = connections.db_session.query(Files).filter(
        Files.closet_id == closet_id, Files.category == category).all()
    for f in files:
        delete_persist(connections, f)


def delete_persist(connections: StorageConnections, obj: Any) -> None:
    # Helper func
    connections.db_session.delete(obj)
    connections.db_session.commit()


def check_user_exists(connections: StorageConnections, username: str) -> bool:
    usr = connections.db_session.query(Users).filter(
        Users.username == username).all()
    return True if usr else False


def query_password(connections: StorageConnections, username: str) -> str:
    usr = connections.db_session.query(Users).filter(
        Users.username == username).all()
    res = ''
    if usr:
        res = usr[0].password_hash
    return res


def query_closet_info(connections: StorageConnections, closet_id: int) -> Dict:
    closet = connections.db_session.query(Closets).filter(
        Closets.closet_id == closet_id).all()
    res = {}
    if closet:
        res = {'closet_name': closet[0].closet_name,
               'username': closet[0].username}
    return res


def query_closet_id(connections: StorageConnections, username: str, closet_name: str) -> List:
    # Returns list since a user may have multiple closets with the same name
    closets = connections.db_session.query(Closets).filter(
        Closets.username == username, Closets.closet_name == closet_name).all()
    res = []
    if closets:
        res = [c.closet_id for c in closets]
    return res


def query_closets_of_user(connections: StorageConnections, username: str) -> List:
    closets = connections.db_session.query(Closets).filter(
        Closets.username == username).all()
    res = []
    if closets:
        res = [{'closet_id': c.closet_id, 'closet_name': c.closet_name} for c in closets]
    return res


def query_all_files_from_closet(connections: StorageConnections, closet_id: int) -> DefaultDict:
    files = connections.db_session.query(Files).filter(
        Files.closet_id == closet_id).all()
    res = defaultdict(list)
    if files:
        for f in files:
            res[f.category].append(
                {'filename': f.filename, 'object_key': f.object_key, 'bucket_name': f.bucket_name})
    return res


def query_all_files_from_closet_category(connections: StorageConnections, closet_id: int, category: str) -> List:
    files = connections.db_session.query(Files).filter(
        Files.closet_id == closet_id, Files.category == category).all()
    res = []
    if files:
        for f in files:
            res.append({'filename': f.filename,
                        'object_key': f.object_key, 'bucket_name': f.bucket_name})
    return res


def query_file_info(connections: StorageConnections, object_key: str) -> Dict:
    file = connections.db_session.query(Files).filter(
        Files.object_key == object_key).all()
    res = {}
    if file:
        res = {'filename': file[0].filename, 'bucket_name': file[0].bucket_name,
               'category': file[0].category, 'closet_id': file[0].closet_id}
    return res


def query_file_key(connections: StorageConnections, closet_id: int, filename: str) -> List:
    # Returns list since a closet may have multiple files with the same name
    file = connections.db_session.query(Files).filter(
        Files.filename == filename, Files.closet_id == closet_id).all()
    res = []
    if file:
        res.append({'object_key': file[0].object_key,
                    'bucket_name': file[0].bucket_name, 'category': file[0].category})
    return res
