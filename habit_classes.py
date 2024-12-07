"""
Class definition module for the Habit Tracker application.

This module contains the class structure definitions for the 
application, including the Habit, Task, and Streak classes.
These models represent the core entities used in the application to track 
user habits and their progress.
"""

from datetime import date
from database import add_habit, add_streak, add_task_checkoff

class Habit:
    """
    A class to represent a habit created by the user.

    Attributes:
    ----------
    title : str 
        The title of the habit.
    descr : str 
        Brief description of the habit.
    freq : str 
        The frequency/periodicity of the habit (e.g., daily, weekly).  
    creation_date : date
        The creation date of the habit.
        Set automatically to current date when object is created.

    Methods 
    ------- 
    __init__(title, descr, freq, creation_date): 
        Declares all the necessary attributes for the habit object and
        adds the habit to the database.
    """
    def __init__(self, title: str, descr: str, freq: str):
        """ 
        Declares all the necessary attributes for the habit object and
        calls the add_habit method (imported from database.py)
        to add the habit to the database.
        Also calls the Streak class constructor to initialize a streak object 
        when a habit is created.
        
        Parameters 
        ---------- 
        title : str 
            The title of the habit. 
        descr : str 
            Brief description of the habit. 
        freq : str 
            The frequency/periodicity of the habit (e.g., daily, weekly). 
        """
        self.title = title
        self.descr = descr
        self.freq = freq
        self.creation_date = date.today()
        add_habit(self)
        # initialize streak object when new habit is created
        Streak(title) 

class Task(Habit):
    """
    A subclass of Habit to represent a single task checkoff for a habit.

    Attributes:
    ----------
    habit_title : str 
        The title of the habit for which the task is checked off.
    checkoff_date : date 
        The checkoff date of the task.
        Set automatically to current date when object is created.

    Methods 
    ------- 
    __init__(habit_title): 
        Declares all the necessary attributes for the task object and
        adds the task checkoff to the database.
    """
    def __init__(self, habit_title: str):
        """
        Declares all the necessary attributes for the task object and
        calls the add_task_checkoff method (imported from database.py)
        to add the task checkoff to the database.

        Parameters 
        ---------- 
        habit_title : str 
            The title of the habit for which the task is checked off.
        """
        self.habit_title = habit_title
        self.checkoff_date = date.today()
        add_task_checkoff(self)

class Streak(Habit):
    """
    A subclass of Habit to represent a streak of consecutive checkoffs
    for a habit.

    Attributes:
    ----------
    habit_title : str 
        The title of the habit for which the streak is tracked.
    counter : int 
        The count value of the streak 
        i.e. number of frequency units the streak has been maintained.
    last_updated : date
        The latest date the counter was updated for the streak.
        Set automatically to current date when object is created.

    Methods 
    ------- 
    __init__(habit_title): 
        Declares all the necessary attributes for the streak object and
        adds the streak to the database.
    """
    def __init__(self, habit_title):
        """
        Declares all the necessary attributes for the streak object and
        calls the add_streak method (imported from database.py)
        to add the streak to the database.

        Parameters
        ----------
        habit_title : str 
            The title of the habit for which the streak is tracked.
        """
        self.habit_title = habit_title
        # default counter value set to 1 (and not 0) to adjust for first checkoff within a streak
        self.counter = 1
        self.last_updated = date.today()
        add_streak(self) 