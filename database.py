"""
Database module for the Habit Tracker application.

This module provides the functionality for establishing a 
database connection and executing SQL queries for the
habit, task, and streak tables.

Functions
---------
set_db_name(str) -> None
    Sets the name of the database to which the application will connect.
get_db(str) -> sqlite3.Connection:
    Establishes connection to local database.
execute_query(str, tuple(optional)) -> None
    Executes a SQL query (except SELECT queries).
execute_select_query(str, tuple(optional)) -> list
    Executes a SQL SELECT query.
create_tables() -> None
    Creates the database tables.
add_habit() -> None
    Adds a new habit to the habit table.
add_task_checkoff() -> None
    Adds a new task checkoff to the task table.
add_streak() -> None
    Adds a new streak to the streak table.
get_all_habits() -> list
    Gets all the habits from the habit table.
get_task_list(str) -> list
    Gets all the task checkoffs for a habit.
get_streak_list(str) -> list
    Gets all the streaks for a habit.
update_streak_counter(str, datetime.date) -> None
    Updates the latest streak counter of a habit.
delete_habit_from_db(str) -> None
    Deletes a habit and all associated entries in task and streak tables.

Notes
-----
- The application relies on the `sqlite3` module for database operations.
"""
import sqlite3

def set_db_name(name: str) -> None:
    """
    Sets the name of the database to which the application will connect.

    Parameters
    ----------
    name : str
        The name of the database.
    
    Returns
    -------
    None
    """
    global db_name 
    db_name = name

def get_db(db_name) -> sqlite3.Connection:
    """
    Establishes connection to local database.

    Parameters
    ----------
    db_name : str
        Name of the database to connect to.

    Returns
    -------
    sqlite3.Connection
        The database connection object.
    """
    db = sqlite3.connect(db_name)
    return db

def execute_query(query: str, values: tuple = None): 
    """
    Executes a SQL query (except SELECT queries).
     
    Prevents redundant code for committing and closing the database
    when executing SQL queries, as well as error handling.
    execute_select_query() is used for SELECT queries.

    Parameters
    ----------
    query : str
        The SQL query to execute.
    values : tuple, optional
        The values to be passed to the SQL query. 

    Returns
    -------
    None
    """
    db = get_db(db_name) 
    cur = db.cursor() 
    try: 
        if values: #if values are passed
            cur.execute(query, values) 
        else: 
            cur.execute(query) 
        db.commit() 
    except Exception as e: 
        print(f"An error occurred: {e}") 
        db.rollback()
    finally: 
        db.close()
    return db

def execute_select_query(query: str, values: tuple = None) -> list: 
    """
    Executes a SQL SELECT query.
     
    Prevents redundant code for committing and closing the database
    when executing SQL SELECT queries, as well as error handling.
    Separated from execute_query() to receive query results
    instead of connection object.

    Parameters
    ----------
    query : str
        The SQL SELECT query to execute.
    values : tuple, optional
        The values to be passed to the SQL query. 

    Returns
    -------
    list
        The query result as a list of rows.
        Each row is represented as a tuple.
    """
    db = get_db(db_name) 
    cur = db.cursor() 
    try: 
        if values: 
            cur.execute(query, values) 
        else: 
            cur.execute(query) 
        results = cur.fetchall() 
        return results 
    except Exception as e: 
        print(f"An error occurred: {e}") 
        return None 
    finally: 
        db.close()

def create_tables() -> None:
    """
    Creates the database tables if they do not already exist.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    # table creation queries for each table
    habit_table_query = """CREATE TABLE IF NOT EXISTS habit(
                        title TEXT PRIMARY KEY,
                        description TEXT,
                        frequency TEXT,
                        creation_date DATE
                    )"""
    task_table_query = """CREATE TABLE IF NOT EXISTS task(
                        habit_title TEXT,
                        checkoff_date DATE,
                        FOREIGN KEY (habit_title) REFERENCES habit(title)
                    )"""
    streak_table_query = """CREATE TABLE IF NOT EXISTS streak(
                        habit_title TEXT,
                        counter INTEGER,
                        last_updated DATE,
                        FOREIGN KEY (habit_title) REFERENCES habit(title)
                    )"""
    # execute table creation queries
    execute_query(habit_table_query) 
    execute_query(task_table_query) 
    execute_query(streak_table_query)

def add_habit(self) -> None:
    """
    Adds a new habit to the habit table in the database.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    add_habit_query = "INSERT INTO habit (title, description, frequency, creation_date) VALUES (?, ?, ?, ?)"
    values = (self.title, self.descr, self.freq, self.creation_date)
    return execute_query(add_habit_query, values)

def add_task_checkoff(self) -> None:
    """
    Adds a new task checkoff to the task table in the database.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    add_task_query = "INSERT INTO task (habit_title, checkoff_date) VALUES (?, ?)" 
    values = (self.habit_title, self.checkoff_date)
    return execute_query(add_task_query, values)

def add_streak(self): 
    """
    Adds a new streak to the streak table in the database.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    add_streak_query = "INSERT INTO streak (habit_title, counter, last_updated) VALUES (?, ?, ?)"
    values = (self.habit_title, self.counter, self.last_updated)
    return execute_query(add_streak_query, values)

def get_all_habits() -> list:
    """
    Gets all the habits from the habit table.

    Parameters
    ----------
    None

    Returns
    -------
    list
        The list of all habits.
        Each habit in the list is represented as a tuple.
    """
    get_habit_query = "SELECT * FROM habit"
    return execute_select_query(get_habit_query)

def get_task_list(habit_title: str) -> list:
    """
    Gets all the task checkoffs for a habit from the task table.

    Parameters
    ----------
    habit_title : str
        The habit for which to retrieve the task checkoff list.

    Returns
    -------
    list
        The list of all task checkoffs for the specified habit.
        Each entry is represented as a tuple.
    """
    get_task_list_query = "SELECT * FROM task WHERE habit_title = ?"
    values = (habit_title,)
    return execute_select_query(get_task_list_query, values)

def get_streak_list(habit_title: str) -> list:
    """
    Gets all the streaks for a habit from the streak table.

    Parameters
    ----------
    habit_title : str
        The habit for which to retrieve the streaks.

    Returns
    -------
    list
        The list of all streaks for the specified habit.
        Each entry is represented as a tuple.
    """
    get_streak_list_query = "SELECT * FROM streak WHERE habit_title = ?"
    values = (habit_title,)    
    return execute_select_query(get_streak_list_query, values)

def update_streak_counter(habit_title: str, date) -> None:
    """
    Updates the latest streak counter of a habit.

    Increments the counter value and updates the date.

    Parameters
    ----------
    habit_title : str
        The habit for which to update the streak.
    date : datetime.date
        The new date to be set.

    Returns
    -------
    None
    """
    # find latest streak counter for given habit title and update the values
    update_streak_query = """UPDATE streak SET counter = counter + 1, last_updated = ?
                WHERE last_updated = (SELECT last_updated FROM streak WHERE habit_title = ? 
                ORDER BY last_updated DESC LIMIT 1)"""
    values = (date, habit_title)
    return execute_query(update_streak_query, values)

def delete_habit_from_db(title: str) -> None:
    """
    Deletes a habit and all associated entries in task and streak tables.

    Parameters
    ----------
    habit_title : str
        The title of the habit to be deleted.
    
    Returns
    -------
    None
    """
    # deletion queries for each occurence of the habit in all tables
    delete_habit_query = "DELETE FROM habit WHERE title = ?"
    delete_task_query = "DELETE FROM task WHERE habit_title = ?"
    delete_streak_query = "DELETE FROM streak WHERE habit_title = ?"
    values = (title,)
    
    execute_query(delete_habit_query, values)
    execute_query(delete_task_query, values)
    execute_query(delete_streak_query, values)
