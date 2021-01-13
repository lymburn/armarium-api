from flask import g
from model.closet_entry_model import ClosetEntry
import typing
from typing import List, Set, Dict, Tuple, Optional
import sqlite3
from sqlite3 import Error
import boto3
from botocore.exceptions import ClientError
import networkx as nx
from networkx.readwrite import json_graph
import json
import uuid
import os
import io

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

def create_tables(connections):
    # Create tables: Users, Closets, Files
    sql_cmd = '''CREATE TABLE IF NOT EXISTS Users (
                    Username text NOT NULL,
                    PasswordHash text NOT NULL,
                    PRIMARY KEY (Username));'''
    execute_sql(connections, sql_cmd)

    sql_cmd = '''CREATE TABLE IF NOT EXISTS Closets (
                    ClosetID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Username text NOT NULL,
                    ClosetName text NOT NULL,
                    FOREIGN KEY (Username) REFERENCES Users(Username));'''
    execute_sql(connections, sql_cmd)

    sql_cmd = '''CREATE TABLE IF NOT EXISTS Files (
                    Filename text NOT NULL,
                    BucketName text NOT NULL,
                    ObjectKey text NOT NULL,
                    Category text NOT NULL,
                    ClosetID INTEGER NOT NULL,
                    PRIMARY KEY (ObjectKey),
                    FOREIGN KEY (ClosetID) REFERENCES Closets(ClosetID));'''
    execute_sql(connections, sql_cmd)
    
    print(f"Created tables: Users, Closets, Files")

def insert_entry(connections, table_name: str, columns, items):
    # Format for items: [ItemForColA, ItemB, ItemC] following order of columns in schema
    cols = ''
    values = ''

    for col in columns:
        cols += col + ', '

    for val in items:
        values += sql_query_str_format(val) + ', '
    
    values = values[:len(values)-2]    
    cols = cols[:len(cols)-2]  

    sql_cmd = 'INSERT INTO ' + table_name + '(' + cols + ')' + ' VALUES (' + values + ');'
    execute_sql(connections.cursor(), sql_cmd)
    connections.commit()

def delete_entry(connections, table_name: str, condition_column: str, condition_value):
    # Condition_value can be any type as specified by table schema
    # Currently checking for int for different SQL query format
    sql_cmd = 'DELETE FROM ' + table_name + ' WHERE ' + condition_column + '=' + sql_query_str_format(condition_value) + ';'
    execute_sql(connections.cursor(), sql_cmd)
    connections.commit()

def update_entry(connections, table_name: str, update_columns: List[str], update_items, condition_column: str, condition_value):
    # Format for items: [ItemForColA, ItemB, ItemC] following order of columns in schema
    # Assumed len(columns) == len(items)
    sql_cmd = 'UPDATE ' + table_name + ' SET '
    temp = ''
    for col, it in zip(update_columns, update_items):
        temp += col + '=' + sql_query_str_format(it) + ', '
    
    where_condition = ' WHERE ' + condition_column + '=' + sql_query_str_format(condition_value) + ';'
    sql_cmd += temp[:len(temp)-2] + where_condition
    execute_sql(connections.cursor, sql_cmd)
    connections.commit()

def select_entry_from_table(connections, table_name: str, condition_columns: List[str], condition_values):
    # Can also be used to check if something exists
    sql_cmd = 'SELECT * FROM ' + table_name + ' WHERE '
    temp = ''
    for col, val in zip(condition_columns, condition_values):
        print(sql_query_str_format(val))
        temp += col + '=' + sql_query_str_format(val) + ' AND '
    sql_cmd += temp[:len(temp)-5] + ';'
    print(sql_cmd)
    cursor = connections.cursor()
    execute_sql(cursor, sql_cmd)
    rv = cursor.fetchall()
    return (rv[0] if rv else None) if None else rv

def select_file_given_user_closet_and_filename(connections, username: str, closet_id: int, filename: str):
    sql_cmd = '''SELECT Files.* FROM Files INNER JOIN Closets 
                    ON Files.ClosetID=Closets.ClosetID 
                    WHERE Closets.Username='''
    sql_cmd += sql_query_str_format(username) + ' AND Closets.ClosetID=' + sql_query_str_format(closet_id)
    sql_cmd += ' AND Files.Filename=' + sql_query_str_format(filename) + ';'
    execute_sql(connections, sql_cmd)
    return connections.db_cursor.fetchall()

def select_all_files_given_user_and_closet(connections, username: str, closet_id: int):
    sql_cmd = '''SELECT Files.* FROM Files INNER JOIN Closets 
                    ON Files.ClosetID=Closets.ClosetID 
                    WHERE Closets.Username='''
    sql_cmd += sql_query_str_format(username) + ' AND Closets.ClosetID=' + sql_query_str_format(closet_id) + ';'
    execute_sql(connections, sql_cmd)
    return connections.db_cursor.fetchall()

def select_all_files_given_user_closet_and_category(connections, username: str, closet_id: int, category: str):
    sql_cmd = '''SELECT Files.* FROM Files INNER JOIN Closets 
                    ON Files.ClosetID=Closets.ClosetID 
                    WHERE Closets.Username='''
    sql_cmd += sql_query_str_format(username) + ' AND Closets.ClosetID=' + sql_query_str_format(closet_id)
    sql_cmd += ' AND Files.Category=' + sql_query_str_format(category) + ';'
    execute_sql(connections, sql_cmd)
    return connections.db_cursor.fetchall()

def sql_query_str_format(value):
    # Helper function, detect if value is type # or Str and format SQL query substring accordingly
    sql_str = ''
    if isinstance(value, int) or isinstance(value, float):
        sql_str = str(value)
    else:
        sql_str = '\'' + value + '\''
    return sql_str

def execute_sql(cursor, sql_cmd: str):
    try:
        cursor.execute(sql_cmd)
    except Error as e:
        print(e)
