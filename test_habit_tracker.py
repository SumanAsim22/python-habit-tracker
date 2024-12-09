""" 
Unit test suite for the Habit Tracker application. 

This module contains unit tests for the core functionalities of the Habit Tracker, 
including habit creation, streak management, and analytical functions.

To run these tests, use the following command in the project directory: 
pytest 

Dependencies: 
- pytest 
- datetime 
"""

import pytest
from datetime import date, timedelta
from habit_analytics import (check_streak, count_tasks, delete_habit, filter_habits,
                            get_longest_streak, get_streak_history, update_streak)
from database import (create_tables, execute_query, get_all_habits, 
                      get_streak_list, get_task_list, set_db_name)
from habit_classes import Habit, Task

@pytest.fixture(scope='function')
def setup_method():
    """ 
    Setup fixture to initialize the database and create necessary tables. 
    This fixture runs before each test function. 
    """
    set_db_name('test.db')
    create_tables()
    global habit_title 
    habit_title = 'Test habit'
    yield
    # teardown code that runs after every test function
    delete_habit(habit_title)

def test_add_habit(setup_method):
    """
    Test that a new habit is correctly added to the database. 
    
    This function creates a new habit and verifies that it is present in the database 
    by checking the list of all habits and ensuring a streak entry is created implicitly. 
    
    Asserts: 
    -------
        - The habit is found in the list of all habits in the database. 
        - A streak entry is created in the database for the habit. 
    """
    
    Habit(habit_title, 'Test description', 'Daily')

    # assert habit creation in database
    habits = get_all_habits()
    assert any(habit[0] == habit_title for habit in habits), 'Habit not created successfully'

    # assert streak creation in database
    streak_counter = get_streak_list(habit_title)
    assert streak_counter, \
        'Streak not added successfully - should be implicitly created upon habit creation'

def test_add_task_checkoff(setup_method):
    """ 
    Test that a task checkoff is correctly added to the database. 
    
    This function creates a new habit and adds a task checkoff for the habit, 
    then verifies that the checkoff is present in the database. 

    Asserts: 
    -------
        - The task checkoff is found in the database for the habit. 
    """
    Habit(habit_title, 'Test description', 'Daily')
    # create a task checkoff
    Task(habit_title)

    count = count_tasks(habit_title)
    # one task entry should be found for habit
    assert count == 1, 'Task checkoff not successful'

def setup_streak_data(days_ago=1):
    """ 
    Helper function to set up streak data for testing. 
    
    This function creates a new habit and adds two task checkoffs to set up the expected streak state. 
    It also allows setting the date for the first task checkoff to simulate a past checkoff. 

    Parameters:
    ----------
    days_ago : str
        Number of days ago to set the checkoff date for the first task. 
    """
    Habit(habit_title, 'Test description', 'Daily')  
    
    # create a task to simulate a past checkoff - default value 1 creates 2-day streak
    Task(habit_title)
    # manually set checkoff date for task and last updated date for streak counter to adjust values  
    checkoff_date = date.today() - timedelta(days=days_ago)
    execute_query("UPDATE task SET checkoff_date = ? WHERE habit_title = ?", 
                (checkoff_date, habit_title)) 
    execute_query("UPDATE streak SET last_updated = ? WHERE habit_title = ?", 
                (checkoff_date, habit_title))  

    # create a task checkoff for the current day
    Task(habit_title)             

def test_check_streak_active(setup_method):
    """ 
    Test that the streak status is correctly identified as active. 
    
    This function sets up a habit with two consecutive day task checkoffs 
    and verifies that the streak status is active. 
    
    Asserts:
    ------- 
        - The streak status is identified as active (True). 
    """
    # create 2 consecutive day task checkoffs
    setup_streak_data()

    streak_status = check_streak(habit_title)
    # streak check for habit should return true i.e. streak status is active
    assert streak_status, 'Streak status error - should return true'

def test_check_streak_inactive(setup_method):
    """ 
    Test that the streak status is correctly identified as inactive. 
    
    This function sets up a habit with two task checkoffs with a one-day gap in between 
    and verifies that the streak status is inactive. 
    
    Asserts: 
    -------
        - The streak status is identified as inactive (False). 
    """
    # create 2 task checkoffs with a one day gap in between
    setup_streak_data(2)

    streak_status = check_streak(habit_title)
    # streak check for habit should return false i.e. streak status is inactive
    assert not streak_status, 'Streak status error - should return false'

def test_update_streak(setup_method):
    """ 
    Test that the streak counter is correctly updated. 
    
    This function sets up a habit with two consecutive day task checkoffs, 
    adds another task checkoff for the current day, and updates the streak. 
    It then verifies that the streak counter is incremented correctly.
    
    Asserts:
    -------
        - The streak counter is incremented correctly to 2. 
    """
    # create 2 consecutive day task checkoffs
    setup_streak_data()
    """
    Create another task checkoff for the current day i.e. total checkoffs = 3 to show
    that additional checkoffs do not contribute towards updating the streak count
    """
    Task(habit_title)
    
    # simulate updating the streak for current day i.e. day 2 of checking off the habit
    update_streak(habit_title)

    streak_count = get_streak_list(habit_title)[0][1]
    # streak counter for habit should return 2 i.e. 2-day streak
    assert streak_count == 2, 'Streak count error - should return 2'

def test_check_streak_weekly(setup_method): 
    """ 
    Test that the streak status is correctly identified as active for a weekly habit. 
    
    This function sets up a habit with two task checkoffs with a 7-day gap in between, 
    updates the habit frequency to weekly, and verifies that the streak status is active. 
    
    Asserts:
    -------
        - The streak status is identified as active (True) for a weekly habit. 
    """
    # create 2 task checkoffs with a 7 day gap in between
    setup_streak_data(7)
    # manually update habit frequency to weekly
    execute_query("UPDATE habit SET frequency = ? WHERE title = ?", ('Weekly', habit_title))

    streak_status = check_streak(habit_title)
    # streak check for habit should return true i.e. weekly streak is active
    assert streak_status, 'Streak status error - should return true'

def test_filter_habits(setup_method):
    """ 
    Test filtering of the habit list based on various parameters. 
    
    This function sets up a habit and filters the habit list by daily habits, 
    active streaks, and habits with at least 4 task checkoffs. 
    It verifies that the habit appears in the appropriate lists. 
    
    Asserts:
    -------
        - The habit is in the lists of daily and active habits. 
        - The habit is not in the list of habits with at least 4 checkoffs. 
    """
    setup_streak_data()

    # get list of all daily habits
    daily_habits = filter_habits('Daily')
    # get list of all habits with an active streak
    active_habits = filter_habits('Active')
    # get list of all habits with at least 4 task checkoffs
    four_count_filter = filter_habits(4)

    assert habit_title in daily_habits and \
           habit_title in active_habits and not \
           habit_title in four_count_filter,\
        'Function error - habit should be in list of daily and active habits'

def test_get_longest_streak(setup_method):
    """ 
    Test getting the longest streak maintained for a habit. 
    
    This function sets up a habit, updates the streak, and verifies 
    that the longest streak is correctly identified. 
    
    Asserts:
    -------
        - The longest streak for the habit is correctly identified as 2. 
    """
    setup_streak_data()
    update_streak(habit_title)

    longest_streak = get_longest_streak(habit_title)
    assert longest_streak == 2, 'Function error - longest streak for habit should be 2'

def test_get_streak_history(setup_method):
    """ 
    Test getting the streak history for a habit. 
    
    This function sets up a habit, updates the streak, and retrieves the streak history. 
    It verifies that the first checkoff is in the list of start dates and the latest checkoff 
    is in the list of end dates. 
    
    Asserts:
    -------
        - The first checkoff date is in the list of start dates. 
        - The latest checkoff date is in the list of end dates. 
    """
    setup_streak_data()
    update_streak(habit_title)

    task_list = get_task_list(habit_title)
    count = count_tasks(habit_title)
    streak_list = get_streak_list(habit_title)

    start_date, last_updated = get_streak_history(habit_title)
    assert task_list[count-2][1] in start_date and streak_list[0][2] in last_updated,\
            'Function error - streak start and end values should be found in lists'

def test_delete_habit(setup_method):
    """ 
    Test that a habit and its related entries are correctly deleted from the database. 
    
    This function creates a habit, adds a task checkoff, and then deletes the habit. 
    It verifies that the habit and its related streak and task entries are removed from the
    corresponding database tables. 
    
    Asserts:
    -------
        - The habit is deleted from the list of all habits. 
        - The streak entry for the habit is deleted. 
        - The task entries for the habit are deleted. 
    """
    Habit(habit_title, 'Test description', 'Daily')
    Task(habit_title)

    delete_habit(habit_title)

    habits = get_all_habits()
    streaks = get_streak_list(habit_title)
    tasks = get_task_list(habit_title)

    # assert complete deletion of the habit from all database tables
    assert not any(habit[0] == habit_title for habit in habits) and streaks == [] and tasks == [],\
            'Habit entries should be deleted from all tables'