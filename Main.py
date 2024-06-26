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

#create_connection() creates the connection to the db
#source: https://www.sqlitetutorial.net/sqlite-python/creating-database/
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

# 5 descripton: Find all competitions (calls for grant proposals) open at a user-specified month, 
# which already have at least one submitted large proposal. 
# For a proposal to be large, it has to request more than $20,000 or to have more than 10 participants, 
# including the principle investigator. Return both IDs and the titles.
def competitions_specific_month(conn):
    print("You have chosen option 5, find all open competitions which have at least one submitted large proposal.")
    month = input("Enter a month (value from 1-12): ")

    list = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]
    while(month not in list):
        print("Sorry, that is not a valid month, please input a value from 01-12")
        month = input("Enter a month (please put a 0 before the number if it is a single digit): ")
        print()

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
               ( Grant_Proposals.requested_amount > 20000 AND Grant_Proposals.application_status= "submitted") OR
                (SELECT COUNT(*) FROM Collaborators WHERE Collaborators.grant_proposal_ID = Grant_Proposals.grant_proposal_ID) > 10
            )
        )
        """.format(date)
        try: 
            cur.execute(month_query)
            rows = cur.fetchall()
            if (len(rows) == 0):
                print("sorry there are no open competitions with at least one large submitted proposal")
            else:
                for row in rows:
                    print(row)
        except Error as e:
            print("Error retrieving records for the specified month :( ") 
    
# 1 Description: For a user specified area, find the proposals that request the largest amount of money 
def user_specified_area(conn):
    print("------------------------------------------------------")
    print("You have chosen option 1, Find the proposals that request the largest amount of money")
    print("Please choose on of the areas of study: ")
    print("Medical, Engineering, Aerodynamics, Agriculture, Big Data, Environmental, Computer Science, Sociology")

    list = ["Medical", "Engineering", "Aerodynamics", "Agriculture", "Big Data", "Environmental", "Computer Science", "Sociology"]
    
    area = input("Enter an area: ")
    print()

    while (area not in list):
        print("Sorry that is not a valid area of study")
        print("Please choose on of the areas of study:")
        print("Medical, Engineering, Aerodynamics, Agriculture, Big Data, Environmental, Computer Science, Sociology")
        area = input("Enter an area: ")
        print()

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
            if(len(rows) == 0 ):
                print("Sorry there's no records found for the specified area")
            for row in rows:
                print(row)
        except Error as e:
            print("Error retrieving records for the specified area :( ")
        
        print("------------------------------------------------------")

# Description: For a user-specified date,  find the proposals submitted before that 
# date that are awarded the largest amount of money.
def user_specified_date(conn):
    print("You have chosen option 2, for a specified date, find the proposals submitted before that date that are awarded the largest amount of money")
    date = input("Enter a date (YYYY-MM-DD): ")
    print()
    with conn:
        cur = conn.cursor()
        # 
        date_query = """ 
        SELECT * FROM Grant_Proposals JOIN Grants ON Grant_Proposals.competition_ID = Grants.competition_ID 
        JOIN Awarded ON Grant_Proposals.grant_proposal_ID = Awarded.grant_proposal_ID 
        WHERE Grants.app_deadline < "{}"  AND
        NOT EXISTS (
            SELECT 1 FROM Grant_Proposals GP_2 JOIN Grants Grants2 ON GP_2.competition_ID = Grants2.competition_ID
            JOIN Awarded Awarded2 ON GP_2.grant_proposal_ID = Awarded2.grant_proposal_ID
            WHERE Grants2.app_deadline < "{}" AND GP_2.amount_awarded > Grant_Proposals.amount_awarded
            AND GP_2.grant_proposal_ID != Grant_Proposals.grant_proposal_ID
        )
        """.format(date,date)
        try: 
            cur.execute(date_query)
            rows = cur.fetchall()
            if(len(rows) == 0 ):
                print("Sorry there's no records found for the specified date")
            for row in rows:
                print(row)
        except Error as e:
            print("Error retrieving records for the specified date :( ")

# Description: For an area specified by the user, output its average requested/awarded discrepancy, 
# that is, the absolute value of the difference between the amounts.
def average_discrepancy(conn):
    print("You have chosen option 3, for an area, find the average requested/awarded discrepancy")
    print("Choose from the following areas of study:")
    print("Aerodynamics, Agriculture, Environmental, Sociology")
    area = input("Enter an area: ")
    print()
    list = ["Aerodynamics", "Agriculture", "Environmental",  "Sociology"]

    while (area not in list):
        print("That is not a valid area of study, please input on of the following")
        print("Aerodynamics, Agriculture, Environmental, Computer Science, Sociology")
        area = input("Enter an area: ")
        print()

    with conn:
        cur = conn.cursor()
        discrepancy_query = """
            SELECT AVG(Grant_Proposals.requested_amount - Grant_Proposals.amount_awarded) FROM Grant_Proposals 
            JOIN Awarded ON Grant_Proposals.grant_proposal_ID = Awarded.grant_proposal_ID JOIN Grants ON Grant_Proposals.competition_ID = Grants.competition_ID
            WHERE Grants.topic = "{}"
        """.format(area)
        try:
            cur.execute(discrepancy_query)
            rows = cur.fetchall()  
            if(rows[0][0]) is None:
                return 
            for row in rows:
                print(row)
        except Error as e: 
            print("Error retrieving records for the specified area :( ")

# Description: For a user-specified name,  find the proposal(s) he/she needs to review
def proposals_by_name(conn):
    print("You have chose option 4, for a specified name, find the proposal he/she needs to review")
    name = input("Enter a name:").split()
    print()

    first_name = name[0]
    last_name = name[1]

    with conn:
        cur = conn.cursor()
        name_query = """
            SELECT Reviewers.first_name, Reviewers.last_name, Grant_Proposals.grant_proposal_ID, Grants.title FROM Reviewers 
            JOIN Assigned ON Reviewers.reviewer_ID = Assigned.reviewer_ID JOIN Assignment ON Assigned.assignment_ID = Assignment.assignment_ID
            JOIN Grant_Proposals ON Assignment.grant_proposal_ID = Grant_Proposals.grant_proposal_ID JOIN Grants ON Grant_Proposals.competition_ID = Grants.competition_ID
            WHERE Reviewers.first_name = "{}" AND Reviewers.last_name = "{}" AND Assignment.submitted = false
        """.format(first_name,last_name)
        try:
            cur.execute(name_query)
            rows = cur.fetchall()
            for row in rows:
                print(row)
        except Error as e:
            print(e)
            print("Error retrieving records for the specified name :( ")

def assign_set_of_reviewers(conn):
    grant_proposal_ID = input("Enter a grant proposal ID:")
    with conn:
        cur = conn.cursor()
        grant_competition_query = """
            SELECT Grant_Proposals.competition_ID, Grants.app_deadline FROM Grant_Proposals JOIN Grants WHERE grant_proposal_ID = "{}"
            """.format(grant_proposal_ID)
        cur.execute(grant_competition_query)
        competition_row = cur.fetchone()
        deadline = competition_row[1]
        assignment_query = """
            SELECT * FROM Assignment WHERE grant_proposal_ID = "{}"
            """.format(grant_proposal_ID)
        cur.execute(assignment_query)
        assignment_rows = cur.fetchone()
        print()
        if(assignment_rows is None):
            create_assignment_query = """
            INSERT INTO Assignment(grant_proposal_ID,num_of_reviewers,deadline,submitted) 
            VALUES ("{}",0,"{}", false)
            """.format(grant_proposal_ID,deadline)
            cur.execute(create_assignment_query)
            print("CREATED ASSIGNMENT")
            cur.execute(assignment_query)
            assignment_rows = cur.fetchone()
            conn.commit() 
        else:
            if(assignment_rows[4] == True):
                print("This assignment has already been submitted")
                return
        assignment_ID = assignment_rows[0]
        possible_reviewers_query = """
        SELECT * FROM Reviewers WHERE Reviewers.grant_applications_reviewed <= 3
        AND NOT EXISTS (
            SELECT 1 FROM Collaborators JOIN Researchers ON Collaborators.researcher_ID = Researchers.researcher_ID  WHERE Collaborators.grant_proposal_ID = "{}"
            AND EXISTS (SELECT 1 FROM conflict_researchers WHERE 
            (conflict_researchers.researcher_ID1 = Collaborators.researcher_ID AND conflict_researchers.researcher_ID2 = Reviewers.reviewer_ID) 
            OR (conflict_researchers.researcher_ID2 = Collaborators.researcher_ID AND conflict_researchers.researcher_ID1 = Reviewers.reviewer_ID)
            OR Reviewers.institution = Researchers.organization)
            AND EXISTS (SELECT 1 FROM Assigned WHERE Assigned.reviewer_ID = Reviewers.reviewer_ID AND Assigned.assignment_ID = "{}"))
        """.format(grant_proposal_ID, assignment_ID)

        try:
            cur.execute(possible_reviewers_query)
            rows = cur.fetchall()
            another_reviewer_bool = True
            while(len(rows) >= 0 and another_reviewer_bool == True):

                
                print("Available reviewers:")
                for row in rows:
                    print(row)
                reviewer_ID = input("Enter a reviewer ID or -1 to cancel: ")
                if(reviewer_ID == "-1"):
                    break
                if(check_in_rows(rows,reviewer_ID) == False):
                    print("Not a valid reviewer ID, please enter a valid reviewer ID")
                    continue
                else:
                    add_reviewer_query = """
                    INSERT INTO Assigned(reviewer_ID, assignment_ID) VALUES ("{}", "{}")
                    """.format(reviewer_ID, assignment_ID)

                    update_reviewers_query = """
                    UPDATE Reviewers SET grant_applications_reviewed = grant_applications_reviewed + 1 WHERE reviewer_ID = "{}"
                    """.format(reviewer_ID)

                    update_assignment_query = """
                    UPDATE Assignment SET num_of_reviewers = num_of_reviewers + 1 WHERE assignment_ID = "{}"
                    """.format(assignment_ID)
                    
                    cur.execute(update_assignment_query)
                    cur.execute(update_reviewers_query)
                    cur.execute(add_reviewer_query)

                    print("Reviewer Added to the assignment")
                    conn.commit()
                    add_another_reviewer = input("Would you like to add another reviewer? (Y/N)")
                    if(add_another_reviewer == "N" or add_another_reviewer == "n"):
                        another_reviewer_bool = False      
                    else:
                        cur.execute(possible_reviewers_query)
                        rows = cur.fetchall()   
        except Error as e:
            print(e)
            print("Error retrieving records :( ")    
    return

def check_in_rows(rows,reviewer_ID):
    for row in rows:
        if(row[0] == int(reviewer_ID)):
            return True
    return False

# def reset_data(conn):
#     with conn:
#         cur = conn.cursor()
#         delete_assigned_values = """ DELETE FROM Assigned """
#         delete_assignment_values = """ DELETE FROM Assignment """
#         delete_participant_values = """ DELETE FROM Participants_table """

#         reassign_participants = """
#             INSERT INTO Participants_Table (meeting_ID, reviewer_ID)
#             VALUES (2410, 1),  (2408, 2), (2304, 3), (2416, 7134), (2411, 2863), (2401, 1238), (2311, 1342),
#             (2409, 3094),(2110, 8945),(2306, 2308); """

#         try:
#             cur.execute(delete_assigned_values)
#             cur.execute(delete_assignment_values)
#             cur.execute(delete_participant_values)
#             cur.execute(reassign_participants)
#             conn.commit()
#             print("Deleting data...")
#         except Error as e:
#             print(e)
#             print("Error deleting records :( ")    


def main():
    database = "council.db"

    conn = create_connection(database)
    print()
    print("Welcome to Council Database. If this is your first time using this program, please choose option 7 before choosing option 6")
    print("if you would like to reassign all reviewers.")
    print()
    x = 10
    while x != 0:
        print("0: Quit")
        print("1: Find the proposals that request the largest amount of money")
        print("2: Find the proposals submitted before the date that are awarded the largest amount of money")
        print("3: Find the average requested/awarded discrepancy")
        print("4: Find the proposals that need to be reviewed with a given name")
        print("5: Find all open competitions that have at least one large submitted proposal(20,000 or more requested)")
        print("6: Reviewer Assignment")

        print()

        x = int(input("Please enter the number of the option you want to go to: "))
        if x > 7:
            print("Sorry that is an invalid number, please input a valid number between 0 and 6")
            print()

        match x:
            case 1: 
                user_specified_area(conn)
            case 2:
                user_specified_date(conn)
            case 3:
                average_discrepancy(conn)
            case 4:
                proposals_by_name(conn)
            case 5: 
                competitions_specific_month(conn)
            case 6:
                assign_set_of_reviewers(conn)

    print("quitting program...")

if __name__ == "__main__":
    main()
