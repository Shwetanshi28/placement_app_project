import sys
import logging
import mysql.connector
from mysql.connector import Error

class DatabaseManager:
    def __init__(self,host,user,password,database):
        """
        Initialize connection variable
        """
        self.host=host
        self.user=user
        self.password=password
        self.database=database
        self.connection=None
        self.cursor=None
        self.connect()

    def connect(self):
        """
        Connect to MySQL Database
        """
        try:
            logging.debug("Trying to connect to MySQL database")
            
            self.connection=mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database 
            )
            self.cursor=self.connection.cursor()

            logging.debug("Connected to the database successfully!")

        except Error as e:
            logging.error(f"Error while connecting to the database: {e}")
            self.connection = None
            self.cursor = None

        finally:
            print("Connect method completed")
           

    def disconnect(self):
        """
        Disconnect to MySQL database
        """
        if self.connection:
            self.cursor.close()
            self.connection.close()
            logging.debug("Disconnected from the Database")


    def execute_query(self,query,data=None):
        """
        Execute INSERT/UPDATE/DELETE Queries
        """
        try:
            self.cursor.execute(query,data)
            self.connection.commit()
            print("Query executed successfully")
        except Error as e:
            print("Error while executing query:",e)

    def fetch_query(self,query,data=None):
        """
        Execute SELECT Queries and return all rows
        Accept optional data for queries with parameter
        """
        try:
            if data:
                self.cursor.execute(query,data)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except Error as e:
            print("Error while fetching data",e)
            return []


    def get_student_details(self, student_id):
        query = """
            SELECT
                P.language,
                P.problems_solved,
                P.assessments_completed,
                P.mini_projects,
                P.certifications_earned,
                P.latest_project_score,

                /*Soft Skills*/ 
                SS.communication,
                SS.teamwork,
                SS.presentation,
                SS.leadership,
                SS.critical_thinking,
                SS.interpersonal_skills,

                /*Placements*/
                PL.mock_interview_score,
                PL.internships_completed,
                PL.placement_status,
                PL.company_name,
                PL.placement_package,
                PL.interview_rounds_cleared,
                PL.placement_date

                FROM students AS S 
                LEFT JOIN Programming AS P ON S.student_id = P.student_id
                LEFT JOIN Soft_skills AS SS ON S.student_id = SS.student_id
                LEFT JOIN Placements AS PL ON S.student_id = PL.student_id

                WHERE S.student_id = %s
        """
        print("Running get_student_details for ID:", student_id )
        print("Query:", query)
        print("With data:", (student_id,))

        result = self.fetch_query(query, (student_id,))
        print("Result:", result)
        return result
        











                