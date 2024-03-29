# Main.py
# 
# This program will display information from a database. 
# You can: 
# find all competitions which already have at least one submitted large proposal,
# find proposals that request the largest amount of money,
# find proposals submitted befoe a certain date that are awarded the largest amt of money,
# find the average requested/awarded discrepancy,
# search for a name and find the proposals they need to view,
# and assign a set of reviewers to review specific grant applications one proposal at a time

import sqlite3
from sqlite3 import Error

# source code: https://www.sqlitetutorial.net/sqlite-python/sqlite-python-select/

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn

def main():
    database = "\council.db"

    conn = create_connection(database)