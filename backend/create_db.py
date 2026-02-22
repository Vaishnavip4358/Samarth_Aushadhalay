import mysql.connector
from mysql.connector import errorcode

# --- IMPORTANT ---
# Replace 'your_password' with your MySQL root password.
# You can also change the user if you are not using root.
USER = 'root'
PASSWORD = 'Vaishnavi@4358' 
HOST = 'localhost'

DB_NAME = 'samarth_aushadhalay_db'

def create_database():
    """This function connects to MySQL and creates the database if it does not exist."""
    try:
        # Connect to MySQL server
        cnx = mysql.connector.connect(user=USER, password=PASSWORD, host=HOST)
        cursor = cnx.cursor()

        # Create database
        try:
            cursor.execute(f"CREATE DATABASE {DB_NAME} DEFAULT CHARACTER SET 'utf8'")
            print(f"Database '{DB_NAME}' created successfully.")
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_DB_CREATE_EXISTS:
                print(f"Database '{DB_NAME}' already exists.")
            else:
                print(err)
        finally:
            cursor.close()
            cnx.close()

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    else:
        print("OK")

if __name__ == '__main__':
    create_database()
