"""
Analysis module for the Habit Tracker application.

This module provides the functionality for managing and analysing 
habits, tasks, and streaks. 

Functions
---------
count_tasks(str) -> str
    Counts the number of task checkoffs for a given habit.
check_streak(str) -> bool
    Checks the streak status for a given habit.
check_daily_streak(list) -> bool
    Checks for a daily streak based on a given list of dates.
check_weekly_streak(list) -> bool
    Checks for a weekly streak based on a given list of dates.
update_streak(str) -> None
    Updates the active streak counter associated with a given habit.
get_active_streak_counter(str) -> tuple
    Gets the active streak counter associated with a given habit.
delete_habit(str) -> None
    Deletes the habit with the given title.
filter_habits(str or int)) -> list
    Filters habits based on the provided filter criteria.
get_longest_streak(str)
    Gets the longest streak for the given habit.
get_streak_history(str) -> tuple
    Generates the streak history for the given habit, with start and end dates.
"""

from datetime import date, timedelta, datetime
from database import (get_task_list, get_all_habits, get_streak_list, 
                      update_streak_counter, delete_habit_from_db)
from habit_classes import Streak

def count_tasks(habit_title: str) -> int:
    """
    Counts the number of task checkoffs for a given habit.

    Parameters
    ----------
    habit_title : str 
        The title of the habit for which the tasks are to be counted.

    Returns
    -------
    int
        The number of tasks for the specified habit.
    """
    tasks = get_task_list(habit_title)
    return tasks.__len__()

def check_streak(habit_title: str) -> bool:
    """
    Checks the streak status for a given habit.

    Parameters
    ----------
    habit_title : str 
        The title of the habit for which the streak status is to be checked.

    Returns
    -------
    bool
        True if streak is active and False if not.
    """
    # set default streak value
    streak = False
    count = count_tasks(habit_title) 
    
    # execute streak check only if habit has been checked off at least once
    if count > 1: 
        task_list = get_task_list(habit_title)
        # populate date list with task checkoff dates (convert date objects to string values to allow accurate comparison) 
        date_list = [datetime.strptime(task[1], '%Y-%m-%d').date() for task in task_list]
        # find corresponding habit title in habit list and retrieve frequency (i.e. habit[2])
        habit_list = get_all_habits()
        habit_freq = next(habit[2] for habit in habit_list if habit_title == habit[0])
        if habit_freq == 'Daily':
            streak = check_daily_streak(date_list)
        else: # habit_freq == 'Weekly'
            streak = check_weekly_streak(date_list)
    else: 
        streak = False
    return streak

def check_daily_streak(date_list: list) -> bool:
    """
    Checks for a daily streak based on a given list of dates.

    Parameters
    ----------
    date_list : list 
        The list of dates for which the daily streak is to be checked.

    Returns
    -------
    bool
        True if daily streak is active and False if not.
    """
    today = date.today()
    yesterday = today - timedelta(days=1)
    day_before_yesterday = today - timedelta(days=2)
    # check if habit was checked off yesterday and either the day before yesterday or today
    return True if yesterday in date_list and \
            any(date_value in date_list for date_value in [day_before_yesterday, today]) \
            else False

def check_weekly_streak(date_list: list) -> bool:
    """
    Checks for a weekly streak based on a given list of dates.

    Parameters
    ----------
    date_list : list 
        The list of dates for which the weekly streak is to be checked.

    Returns
    -------
    bool
        True if weekly streak is active and False if not.
    """
    today = date.today()  
    # find the most recent monday -- monday = 0 and sunday = 6 
    last_monday = today - timedelta(days=today.weekday())
    # generate a list of dates for the week before last
    week_before_last_dates = [last_monday - timedelta(days=i) for i in range(8, 15)]
    # generate a list of dates for the last week
    last_week_dates = [last_monday - timedelta(days=i) for i in range(1, 8)] 
    # generate a list of dates for the current week 
    current_week_dates = [last_monday + timedelta(days=i) for i in range(7)]
    # check if habit was checked off during the last week and either the week before last or the current week
    last_week_found = True if any(date_value in last_week_dates for date_value in date_list) else False
    consecutive_week_dates = week_before_last_dates + current_week_dates #concatenate lists
    return True if last_week_found \
            and any(date_value in date_list for date_value in consecutive_week_dates) \
            else False

def update_streak(habit_title: str) -> None:
    """
    Updates the active streak counter associated with a given habit.

    Parameters
    ----------
    habit_title : str
        The title of the habit for which the streak is to be updated.

    Returns
    -------
    None
    """
    # get latest streak counter from streak counter list
    active_streak_counter = get_active_streak_counter(habit_title) 
    if check_streak(habit_title):
        # get last updated date value and convert to date object for accurate comparison
        last_updated_str = active_streak_counter[2] 
        last_updated = datetime.strptime(last_updated_str, '%Y-%m-%d').date()
        # find corresponding habit title in habit list and retrieve frequency (i.e. habit[2])
        habit_list = get_all_habits()
        habit_freq = next(habit[2] for habit in habit_list if habit_title == habit[0])

        # if daily freqeuncy
        today = date.today()  
        # update counter if streak has not already been updated today
        if habit_freq == 'Daily' and last_updated != today: 
            update_streak_counter(habit_title, today)

        else: # if weekly frequency
            # find the most recent monday -- monday = 0 and sunday = 6 
            last_monday = today - timedelta(days=today.weekday())
            current_week_dates = [last_monday + timedelta(days=i) for i in range(7)]
            # update counter if streak has not already been updated within the current week
            if last_updated not in current_week_dates: 
                update_streak_counter(habit_title, today)

    elif active_streak_counter[1] > 1: 
        """
        If the habit streak is False but the streak counter is 1, then no changes have to 
        be made because the current counter can still be used.
        However, if the streak is False but the counter is greater than 1, 
        this means that the counter was used but the streak is now broken.
        In this case, a new streak object is created.
        The previous streak counter(s) thus maintain a record of established streaks.
        """
        Streak(habit_title)

def get_active_streak_counter(habit_title: str) -> tuple:
    """
    Gets the active streak counter associated with a given habit.

    Parameters
    ----------
    habit_title : str
        The title of the habit for which the streak counter is to be retrieved.

    Returns
    -------
    tuple
        Database entry representative of active streak counter for specified habit.
    """
    streak_list = get_streak_list(habit_title)
    # get latest streak counter from streak list
    return streak_list[streak_list.__len__()-1] 

def delete_habit(habit_title: str) -> None:
    """
    Deletes the habit with the given title.

    Parameters
    ----------
    habit_title: str
        The title of the habit to be deleted.

    Returns
    -------
    None
    """
    delete_habit_from_db(habit_title)
            
def filter_habits(filter) -> list:
    """
    Filters habits based on the provided filter criteria.

    Parameters
    ----------
    filter
        The filter against which the habits are to be matched.
        Should be a string or an integer.

    Returns
    -------
    list
        A list of habit titles that match the specified filter criteria.

    Notes 
    ----- 
    - If the filter is 'Daily' or 'Weekly', habits are filtered by their frequency value. 
    - If the filter is 'Active' or 'Inactive', habits are filtered by their streak status. 
    - If the filter is a task count, habits are filtered based on the number of task checkoffs.
    """
    # retrieve all habits from the database 
    habit_list = get_all_habits()
    # extract the title value from each tuple in habit_list
    habit_titles = [habit[0] for habit in habit_list]
    matched_list = []

    if filter == 'Daily' or filter == 'Weekly':
        # compare frequency filter with each habit's frequency and add title
        for habit in habit_list:
            if habit[2] == filter: 
                matched_list.append(habit[0]) 
    elif filter == 'Active' or filter == 'Inactive':
        if filter == 'Active': 
            status = True
        else: 
            status = False
        # compare streak status filter with each habit's status and add title
        for title in habit_titles:
            streak_status = check_streak(title)
            if streak_status == status: 
                matched_list.append(title)   
    else: # if filter is Task count
        # compare task count value with each habit's task count and add title
        for title in habit_titles:
            count = count_tasks(title)
            if count >= filter:
                matched_list.append(title)
    return matched_list

def get_longest_streak(habit_title: str):
    """
    Gets the longest streak for the given habit.

    Parameters
    ----------
    habit_title : str
        The title of the habit for which the longest streak is to be retrieved.

    Returns
    -------
    int, set
        (If all habits are to be analysed for longest streak)
        The longest streak across all habits and the corresponding
        set of habits.
    int
        (If a specific habit is to be analysed for longest streak)
        The longest streak for the specified habit.
    """
    # retrieve all habits from the database 
    habit_list = get_all_habits()
    # extract the title value from each tuple in habit_list
    habit_titles = [habit[0] for habit in habit_list]

    if habit_title == 'All':
        max_count = 1
        max_count_titles = []
        for title in habit_titles:
            for streak in get_streak_list(title):
                # iterate through streak counts in list and update max count value
                if streak[1] > max_count:
                    max_count = streak[1]
                    max_count_titles = [title]
                # add corresponding title to list of titles with the max count value
                elif streak[1] == max_count:
                    max_count_titles.append(title)
        if max_count == 1: 
            # if max count is 1, no streak was established and thus, the default value is adjusted to return correct value
            max_count = 0
        # convert list to set to remove duplicates
        return max_count, set(max_count_titles)
    else: # for a specific habit
        streak_list = get_streak_list(habit_title)
        counters = [streak[1] for streak in streak_list]
        max_count = max(counters)
        if max_count == 1: 
            # if max count is 1, no streak was established and thus, the default value is adjusted to return correct value
            max_count = 0
        return max_count

def get_streak_history(habit_title: str) -> tuple:
    """
    Generatres the streak history for the given habit, with start and end dates.

    Parameters
    ----------
    habit_title : str
        The title of the habit for which the streak history is to be generated.

    Returns
    -------
    tuple
        Two lists containing the dates on which streaks were started and the dates
        on which they ended (or were last updated), respectively.
    """
    streak_list = get_streak_list(habit_title)
    # find corresponding habit title in habit list and retrieve frequency (i.e. habit[2])
    habit_list = get_all_habits()
    habit_freq = next(habit[2] for habit in habit_list if habit_title == habit[0])
    #initialize list variables
    streak_start_dates = []
    streak_end_dates = []

    if habit_freq == 'Daily':
        for streak in streak_list:
            # execute only for established streaks
            if streak[1] != 1:
                # get last updated date of the streak as date object
                last_updated = datetime.strptime(streak[2], '%Y-%m-%d').date()
                # get the date on which the streak started
                start_date = last_updated - timedelta(days=streak[1]-1)

                streak_start_dates.append(str(start_date))
                streak_end_dates.append(streak[2])

    else: # if weekly
        for streak in streak_list:
            # get last updated date of the streak as date object
            last_updated = datetime.strptime(streak[2], '%Y-%m-%d').date()
            # get monday's date for the week in which the last update for the streak occured
            monday = last_updated - timedelta(days=last_updated.weekday())
            # get the number of weeks that contributed to the streak
            number_of_weeks = streak[1] 
            # get the list of dates for the week in which the streak started
            streak_start_week = [(monday - timedelta(weeks=number_of_weeks-1)) + timedelta(days=i) for i in range(7)]
            task_list = get_task_list(habit_title)
            for task in task_list:
                # find the date on which the streak started by comparing with task checkoff dates 
                for date in streak_start_week:
                    if task[1] == str(date):
                        # add values to lists once start date is found
                        streak_start_dates.append(task[1])
                        streak_end_dates.append(streak[2])
                        break

    return streak_start_dates, streak_end_dates