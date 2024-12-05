import pytest
from datetime import date, timedelta
from habit_analytics import (check_streak, count_tasks, delete_habit, filter_habits,
                            get_longest_streak, get_streak_history, update_streak)
from database import (create_tables, execute_query, get_all_habits, 
                      get_streak_list, get_task_list, set_db_name)
from habit_classes import Habit, Task

# Fixture for database setup before running a function and deleting test habit after every function
@pytest.fixture(scope='function')
def setup_method():
    set_db_name('test.db')
    create_tables()
    global habit_title 
    habit_title = 'Test habit'
    yield

    # teardown code that runs after every test function
    delete_habit(habit_title)

# Tests for required database entries upon habit creation 
def test_add_habit(setup_method):
    Habit(habit_title, 'Test description', 'Daily')

    # assert habit creation in database
    habits = get_all_habits()
    assert any(habit[0] == habit_title for habit in habits), 'Habit not created successfully'

    # assert streak creation in database
    streak_counter = get_streak_list(habit_title)
    assert streak_counter, \
        'Streak not added successfully - should be implicitly created upon habit creation'

# Test for adding a task checkoff
def test_add_task_checkoff(setup_method):
    Habit(habit_title, 'Test description', 'Daily')
    # create a task checkoff
    Task(habit_title)

    count = count_tasks(habit_title)
    # one task entry should be found for habit
    assert count == 1, 'Task checkoff not successful'

# create the habit and add 2 task checkoffs to set up the expected streak state 
def setup_streak_data(days_ago=1):
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

# Test for checking active streak status
def test_check_streak_active(setup_method):
    # create 2 consecutive day task checkoffs
    setup_streak_data()

    streak_status = check_streak(habit_title)
    # streak check for habit should return true i.e. streak status is active
    assert streak_status, 'Streak status error - should return true'

# Test for checking inactive streak status 
def test_check_streak_inactive(setup_method):
    # create 2 task checkoffs with a one day gap in between
    setup_streak_data(2)

    streak_status = check_streak(habit_title)
    # streak check for habit should return false i.e. streak status is inactive
    assert not streak_status, 'Streak status error - should return false'

# Test for updating streak counter
def test_update_streak(setup_method):
    # create 2 consecutive day task checkoffs
    setup_streak_data()
    # create another task checkoff for the current day i.e. total checkoffs = 3
    Task(habit_title)
    
    # simulate updating the streak for current day i.e. day 2 of checking off the habit
    update_streak(habit_title)

    streak_count = get_streak_list(habit_title)[0][1]
    # streak counter for habit should return 2 i.e. 2-day streak
    assert streak_count == 2, 'Streak count error - should return 2'

def test_check_streak_weekly(setup_method): 
    # create 2 task checkoffs with a 7 day gap in between
    setup_streak_data(7)
    # manually update habit frequency to weekly
    execute_query("UPDATE habit SET frequency = ? WHERE title = ?", ('Weekly', habit_title))

    streak_status = check_streak(habit_title)
    # streak check for habit should return true i.e. weekly streak is active
    assert streak_status, 'Streak status error - should return true'

# Test for filtering the habit list based on various parameters
def test_filter_habits(setup_method):
    setup_streak_data()

    # get list of all daily habits
    daily_habits = filter_habits('Daily')
    # get list of all habits with an active streak
    active_habits = filter_habits('Active')
    # get list of all habits with at least 4 task checkoffs
    four_count_filter = filter_habits(4)

    # Assert that the habit is in the lists of daily and active habits, 
    # but not in the list of habits with at least 4 checkoffs
    assert habit_title in daily_habits and \
           habit_title in active_habits and not \
           habit_title in four_count_filter,\
        'Function error - habit should be in list of daily and active habits'

# Test for getting the longest streak maintained 
def test_get_longest_streak(setup_method):
    setup_streak_data()
    update_streak(habit_title)

    longest_streak = get_longest_streak(habit_title)
    assert longest_streak == 2, 'Function error - longest streak for habit should be 2'

def test_get_streak_history(setup_method):
    setup_streak_data()
    update_streak(habit_title)

    task_list = get_task_list(habit_title)
    count = count_tasks(habit_title)
    streak_list = get_streak_list(habit_title)

    start_date, last_updated = get_streak_history(habit_title)
    # assert that first checkoff is in list of start dates and latest checkoff is in list of end dates  
    assert task_list[count-2][1] in start_date and streak_list[0][2] in last_updated,\
            'Function error - streak start and end values should be found in lists'

# Test for deleting a habit
def test_delete_habit(setup_method):
    Habit(habit_title, 'Test description', 'Daily')
    Task(habit_title)

    delete_habit(habit_title)

    habits = get_all_habits()
    streaks = get_streak_list(habit_title)
    tasks = get_task_list(habit_title)

    # assert complete deletion of the habit from all database tables
    assert not any(habit[0] == habit_title for habit in habits) and streaks == [] and tasks == [],\
            'Habit entries should be deleted from all tables'