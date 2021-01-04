from flask import g
import sqlite3
from sqlite3 import Error
import boto3
from model.closet_entry_model import ClosetEntry

# Database access functions
def connect_to_db(database_path):
    db = getattr(g, '_database', None)
    if db is None:
        try:
            db = g._database = sqlite3.connect(database_path)
            print("Connection to SQLite DB successful")
        except Error as e:
            print(f"The error '{e}' occurred")
    
    db.row_factory = sqlite3.Row
    return db

def get_db():
    db = getattr(g, '_database', None)
    return db

def close_db():
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
        print("Connection to SQLite DB closed")

def create_table(connections, user: str, closet: str):
    table_name = get_table_name(user, closet)
    create_table_sql = 'CREATE TABLE ' + table_name + ''' (
                            filename text PRIMARY KEY,
                            object_key text NOT NULL,
                            category text NOT NULL);''' # NOTE: MVP, May add more columns later on
    execute_sql(connections.cursor(), create_table_sql)
    print(f"Created table {table_name}")

def add_entry(connections, user: str, closet: str, closet_entry: ClosetEntry):
    # TODO: Add !null chk for entry fields
    table_name = get_table_name(user, closet)
    
    filename = closet_entry.filename
    object_key = closet_entry.object_key
    category = closet_entry.category

    sql_cmd = 'INSERT INTO ' + table_name + ' VALUES (\'' + filename + '\', \'' + object_key + '\', \'' + category + '\');'
    execute_sql(connections.cursor(), sql_cmd)
    connections.commit()

def remove_entry(connections, user: str, closet: str, filename: str):
    table_name = get_table_name(user, closet)
    sql_cmd = 'DELETE FROM ' + table_name + ' WHERE filename = \'' + filename + '\';'
    execute_sql(connections.cursor(), sql_cmd)
    connections.commit()

def update_entry(connections, user: str, closet: str, filename: str, object_key=None, category=None):
    table_name = get_table_name(user, closet)
    sql_cmd = ''

    if object_key is not None and category == None:
        sql_cmd = 'UPDATE ' + table_name + ' SET object_key = \'' + object_key + '\' WHERE filename = \'' + filename + '\';'
    elif category is not None and object_key == None:
        sql_cmd = 'UPDATE ' + table_name + ' SET category = \'' + category + '\' WHERE filename = \'' + filename + '\';'
    else:
        sql_cmd = 'UPDATE ' + table_name + ' SET object_key = \'' + object_key + '\', category = \'' + category + '\' WHERE filename = \'' + filename + '\';'
    execute_sql(connections.cursor(), sql_cmd)
    connections.commit()

def select_entries_from_closet(connections, user: str, closet: str):
    table_name = get_table_name(user, closet)
    sql_cmd = 'SELECT * FROM ' + table_name + ';'
    cursor = connections.cursor()
    execute_sql(cursor, sql_cmd)
    return cursor.fetchall()

def select_file_info_from_db(connections, user: str, closet: str, filename: str):
    table_name = get_table_name(user, closet)
    sql_cmd = 'SELECT * FROM ' + table_name + ' WHERE filename = \'' + filename + '\';'
    cursor = connections.cursor()
    execute_sql(cursor, sql_cmd)
    return cursor.fetchall()

def select_entries_from_db_given_category(connections, user: str, closet: str, category: str):
    table_name = get_table_name(user, closet)
    sql_cmd = 'SELECT * FROM ' + table_name + ' WHERE category = \'' + category + '\';'
    cursor = connections.cursor()
    execute_sql(cursor, sql_cmd)
    return cursor.fetchall()

def get_table_name(user: str, closet: str):
    # Assume: username cannot contain whitespace + is unique, closet name is unique for this user
    closet_name = closet.replace(" ", "_")
    username = convert_username_sql_safe(user)
    table_name = username + "_" + closet_name
    return table_name

def convert_username_sql_safe(user: str):
    username = ''

    if len(user) > 128:
        user = user[:128]
        username = user
    if user[0].isalpha() == False:
        # Idk...Temporary measure
        username = 'user_' + user

    return username

def execute_sql(cursor, sql_cmd: str):
    try:
        cursor.execute(sql_cmd)
    except Error as e:
        print(e)