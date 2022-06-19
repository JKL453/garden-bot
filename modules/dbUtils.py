import modules.config as config
from telegram import Update
import psycopg2, datetime

class BotDatabase(object):
    """
    Handles the database connection and queries.
    """
    
    def __init__(self):
        """
        Connect to your postgres database and create a cursor.
        """
        self.conn = psycopg2.connect(config.DATABASE_URL, sslmode='require')
        self.cursor = self.conn.cursor()

    def test_connection(self):
        """
        Test the database connection.
        """
        # Execute a query
        self.cursor.execute("SELECT * FROM users")

        # Retrieve query results
        users = self.cursor.fetchall()    

        # Print query results
        for row in users:
            print("id = ", row[0], )
            print("chat_id = ", row[1])
            print("first_name  = ", row[2], "\n")
        
        #update.message.reply_text('Reading db...')

    def get_user_id(self, user_name):
        """
        Returns the user id for the given user name.
        """
        self.cursor.execute("SELECT id FROM users WHERE name = %s", (user_name,))
        return self.cursor.fetchone()[0]

    def get_user_name(self, user_id):
        """
        Returns the user name for the given user id.
        """
        self.cursor.execute("SELECT name FROM users WHERE id = %s", (user_id,))
        return self.cursor.fetchone()[0]

    def get_all_users(self):
        """
        Returns a list of all users.
        """
        self.cursor.execute("SELECT * FROM users")
        return self.cursor.fetchall()

    def write_database(self, user_name, user_chat_id):
        """
        Write a new user to the database.
        """
        # Create SQL query
        sql_command = (
            "UPDATE users "
            "SET chat_id = {chat_id} ".format(chat_id = user_chat_id) +
            "WHERE first_name = '{first_name}';".format(first_name = user_name)
        )
        
        # Execute query
        self.cursor.execute(sql_command)

        # Make the changes to the database persistent 
        self.conn.commit()

    def get_water_person(self):
        """
        Returns the user name for the user who is responsible for watering the plants.
        """
        # Create SQL query
        sql_read = ("SELECT * FROM tasks;")

        # Execute query
        self.cursor.execute(sql_read)

        sql_data = self.cursor.fetchall()
        last_water_person_id = sql_data[0][1]
        last_watering_date = sql_data[0][2]

        duration =  datetime.datetime.now().date() - last_watering_date
        days_passed = duration.days

        print("days passed: " + str(days_passed))

        if last_water_person_id < 7:
            today_water_person_id = last_water_person_id + days_passed

        else: 
            today_water_person_id = days_passed-1

        # Create SQL query
        sql_update = (
            "UPDATE tasks "
            "SET person_id = {}, ".format(today_water_person_id) +
            "date = '{}'::DATE ".format(datetime.datetime.now().date()) + 
            "WHERE task = 'last_watering';"
        )
        # Execute query
        self.cursor.execute(sql_update)

        # Make the changes to the database persistent 
        self.conn.commit()

        return today_water_person_id

    def close(self):
        """
        Close the database connection.
        """
        self.cursor.close()
        self.conn.close()
        self.conn = None
        self.cursor = None


   



