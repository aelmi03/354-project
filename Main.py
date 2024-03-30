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
def competitions_specific_month(conn):
    month = input("Enter a month (value from 1-12): ")
    date = "2024-{}-01".format(month)
    with conn:
        
        cur = conn.cursor()
        month_query = """ 
        SELECT competition_ID, title FROM Grants
        WHERE app_deadline > "{}"
        AND EXISTS (
            SELECT 1 FROM Grant_Proposals
            WHERE Grant_Proposals.competition_ID = Grants.competition_ID
            AND (
                Grant_Proposals.requested_amount > 20000 OR
                (SELECT 1 FROM Collaborators WHERE Collaborators.grant_proposal_ID = Grant_Proposals.grant_proposal_ID) > 10
            )
        )
        """.format(date)
        try: 
            cur.execute(month_query)
            rows = cur.fetchall()
            for row in rows:
                print(row)
        except Error as e:
            print("Error retrieving records for the specified month :( ")
            
        
    
    
def user_specified_area(conn):
    area = input("Enter an area:")
    with conn:
        cur = conn.cursor()
        area_query = """ 
        SELECT * FROM Grant_Proposals JOIN Grants ON Grant_Proposals.competition_ID = Grants.competition_ID WHERE
        Grants.topic = "{}" AND
        NOT EXISTS (
            SELECT 1 FROM Grant_Proposals GP_2 JOIN Grants Grants2 ON GP_2.competition_ID = Grants2.competition_ID
            WHERE Grants2.topic = "{}" AND GP_2.requested_amount > Grant_Proposals.requested_amount
        )
        """.format(area,area)
        try: 
            cur.execute(area_query)
            rows = cur.fetchall()
            for row in rows:
                print(row)
        except Error as e:
            print("Error retrieving records for the specified area :( ")

def main():
    database = "council.db"

    conn = create_connection(database)
    user_specified_area(conn)

if __name__ == "__main__":
    main()