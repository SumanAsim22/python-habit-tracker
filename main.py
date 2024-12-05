"""
Main module for the Habit Tracker application.

This module serves as the entry point for the Habit Tracker application. 
It initializes the database, defines the main application logic, 
and handles user interactions.

Functions
---------
is_number(str) -> bool
    Verifies whether a value is an integer.
run_application() -> None
    Starts the main application.
"""

import questionary
from rich.console import Console
from rich.style import Style
from rich.table import Table
from habit_analytics import (count_tasks, check_streak, delete_habit, filter_habits, 
                     get_active_streak_counter, get_longest_streak, update_streak)
from database import create_tables, get_all_habits, get_db, set_db_name, get_task_list
from habit_classes import Habit, Task

# style variables for different output types
cancel_style = Style(color='red')
info_style= Style(color='green4', bold=True)
title_style = Style(color='turquoise4', bold=True)
console = Console()

def is_number(value: str) -> bool: 
    """
    Verifies whether a value is an integer.

    Parameters
    ----------
    value : str
        The value to be converted and verified.
    
    Returns
    -------
    bool
        True if value is an integer False if not
    """
    try: 
        int(value) 
        return True 
    except ValueError: 
        return False

def run_application() -> None:
    """
    Starts the main application.

    Asks the user for confirmation before presenting the main menu
    for the next action. The application runs until the user selects 'Exit'. 
    Enables all the application functionality through CLI prompts and menus.
    
    Parameters
    ----------
    None

    Returns
    -------
    None

    Notes
    -----
    Methods from the Questionary and Rich libraries are used for 
    user prompts and formatted outputs, respectively.
    """
    # set database name 
    db_name = questionary.text('Enter database name (e.g. test.db): ', default ='test.db').ask()
    set_db_name(db_name)
    # start database connection and create tables
    get_db(db_name)
    create_tables()
    print(f'Connected to database {db_name}')

    # define option lists for selection menus
    main_menu_options = ['Create new habit', 'Manage habits', 'Analyse habits', 'Exit']
    frequency_options = ['Daily', 'Weekly']
    habit_management_options = ['Checkoff habit', 'Delete habit', 'Return to main menu']
    habit_analysis_options = ['Filter habits', 'Get longest streak', 'Return to main menu']
    filter_options = ['Frequency', 'Streak status', 'Checkoff count', 'Cancel']
    streak_status_options = ['Active', 'Inactive']
 
    # ask user for confirmation before starting the application
    is_user_ready = questionary.confirm('Would you like to start the application?', default=True).ask()
    # continue running the application until user selects 'Exit'
    while is_user_ready:
        # get habit list and titles in every iteration to sync with any updates made in the previous iteration
        habit_list = get_all_habits() 
        habit_titles = [habit[0] for habit in habit_list]
        title_options = habit_titles + ['Cancel']

        print('') # insert blank line
        
        # display the main menu in each iteration
        main_menu = questionary.select('Main menu:', 
                                    choices=main_menu_options).ask()
        # 'Create new habit' option
        if main_menu == 'Create new habit':
            console.print('\n-----New habit form-----', style=title_style)
            # display habit creation form and get individual values
            habit_details = questionary.form(
                title = questionary.text('Enter habit title: ',
                                        # use questionary's validator to prevent empty title
                                        validate=lambda text: True if len(text) > 0 else "Please enter a title"),
                descr = questionary.text('Enter habit description: '),
                freq = questionary.select('Select habit frequency: ', choices=frequency_options)).ask()
            
            # confirm habit creation
            creation_confirmed = questionary.confirm(
                f'Do you want to create the {habit_details['freq']} habit \'{habit_details['title']}\'?').ask()
            if creation_confirmed:
                # check if the habit title already exists
                habit_exists = any(habit_details['title'] == habit[0] for habit in habit_list)
                if habit_exists:
                    console.print('Habit title already exists - please enter a different title', style=cancel_style)
                else:
                    # create new habit object
                    Habit(habit_details['title'], habit_details['descr'], habit_details['freq'])
                    console.print(f'New habit created: {habit_details['title']}', style=info_style)
            else: console.print('Habit creation cancelled by user', style=cancel_style)
        
        # 'Manage habits' option 
        elif main_menu == 'Manage habits':
            # execute if a habit list is retrieved successfully
            if habit_list: 
                for title in habit_titles:
                    if not check_streak(title):
                        update_streak(title) 

                # create and display a table of all habits in the database
                table = Table(title='Habit List')
                table.add_column('Title', justify='left', style='cyan', no_wrap=True)
                table.add_column('Description', style='magenta', no_wrap=True)
                table.add_column('Frequency', style='green', no_wrap=True)
                table.add_column('Current streak', justify='center', style='yellow', no_wrap=True)
                table.add_column('Checkoff count', justify='center', style='dark_orange', no_wrap=True)
                table.add_column('Last checkoff', style='blue', no_wrap=True)
                for habit in habit_list:
                    title, descr, freq, creation_date = habit

                    # get active streak counter to get latest streak count
                    active_counter = get_active_streak_counter(title)
                    if active_counter[1] == 1:
                        """
                        If no streak has been established, the default value is 1 in order
                        to account for the first day of the streak when it starts.
                        However, this value is set to 0 when being displayed to reflect that
                        no streak has been established yet.
                        """
                        streak_count = 0
                    else: 
                        streak_count = active_counter[1]

                    # get number of checkoffs for habit
                    task_count = count_tasks(title) 
                    if task_count > 0:
                        # get latest checkoff date from task list
                        task_list = get_task_list(title)
                        latest_checkoff = task_list[task_list.__len__() - 1][1]
                    else:
                        latest_checkoff = 'No checkoffs'

                    table.add_row(title, descr, freq, str(streak_count), str(task_count), str(latest_checkoff))
                    
                console.print(table)
                console.print('Note: A streak will only be started\
                              \n-> for a daily habit if it has been checked off for two consecutive days\
                              \n-> for a weekly habit if it has been checked off at least once for two consecutive weeks',\
                              style=info_style)

                # display next set of actions relating to user's habit list
                menu = questionary.select('\nWhat would you like to do?', 
                                    choices=habit_management_options).ask()

                # 'Checkoff habit' option
                if menu == 'Checkoff habit':
                    habit_title = questionary.select('Select a habit to checkoff', 
                                        choices=title_options).ask()
                    if habit_title == 'Cancel':
                        console.print('Task checkoff cancelled', style=cancel_style)
                    else: 
                        # create new task object if habit is checked off and update its streak 
                        Task(habit_title)
                        update_streak(habit_title)
                        console.print(f'Habit checked off: {habit_title}', style=info_style)

                # 'Delete habit' option
                elif menu == 'Delete habit':
                    habit_title = questionary.select('Select a habit to delete', 
                                        choices=title_options).ask()
                    if habit_title == 'Cancel':
                        console.print('Habit deletion cancelled by user', style=cancel_style)
                    else:
                        deletion_confirmed = questionary.confirm(
                            'Are you sure you want to delete this habit? This action cannot be reversed!').ask()
                        if deletion_confirmed: 
                            delete_habit(habit_title)
                            console.print(f'Habit \'{habit_title}\' deleted successfully', style=info_style)
                        else: 
                            console.print('Habit deletion cancelled by user', style=cancel_style)
                
                # 'Return to main menu' option
                else: 
                    pass
            else:
                console.print('No habits found', style=cancel_style)

        # 'Analyse habits' option
        elif main_menu == 'Analyse habits':
            # execute if a habit list is retrieved successfully
            if habit_list:
                console.print('\n-----Habit analysis-----', style=title_style)
                analysis_function = questionary.select('Please choose a function:',
                                                choices=habit_analysis_options).ask()
                empty_list_msg = 'No habits found with this filter'

                if analysis_function == 'Filter habits':
                    filter = questionary.select('Select filter: ', choices=filter_options).ask()
                    
                    # find and return habits with the selected frequency
                    if filter == 'Frequency':
                        freq = questionary.select('Select habit frequency: ', choices=frequency_options).ask()
                        matched_list = filter_habits(freq)

                        if matched_list == []: 
                            console.print(empty_list_msg, style=info_style)
                        else: 
                            console.print(f'{freq} habits:' , style=title_style)
                            for title in matched_list:
                                print(title)

                    # find and return habits with the selected streak status
                    elif filter == 'Streak status':
                        status = questionary.select('Select streak status:', 
                                                    choices=streak_status_options).ask()
                        matched_list = filter_habits(status)

                        if matched_list == []: 
                            console.print(empty_list_msg, style=info_style)
                        else: 
                            console.print(f'Habits with {status} streak:' , style=title_style)
                            for title in matched_list:
                                print(title)

                    # find and return habits with task checkoff count at least equal to the specified value
                    elif filter == 'Checkoff count':
                        value = questionary.text('Enter a number (used as minimum value - e.g.: at least 2 checkoffs):',
                                                # verify user-entered value is an integer
                                                validate=lambda value: True if is_number(value) 
                                                else "Please enter a valid number").ask()
                        matched_list = filter_habits(int(value))

                        if matched_list == []: 
                            console.print(empty_list_msg, style=info_style)
                        else: 
                            console.print(f'Habits with at least {value} checkoff/s:', style=title_style)
                            table = Table()
                            table.add_column('Habit', justify='left', style='cyan', no_wrap=True)
                            table.add_column('Count', style='magenta')
                            for title in matched_list:
                                count = count_tasks(title)
                                table.add_row(title, str(count))
                            console.print(table)
                    # 'Cancel' option                        
                    else: 
                        pass

                elif analysis_function == 'Get longest streak': 
                    habit_title = questionary.select('Select a habit for the function:', 
                                        choices=['All']+title_options).ask()

                    if habit_title == 'Cancel':
                        pass
                    elif habit_title == 'All':
                        longest_streak = get_longest_streak(habit_title)
                        console.print(f'\nLongest streak across all habits: {str(longest_streak[0])}', style=info_style)
                        console.print('For habit/s:', style=title_style)
                        for title in longest_streak[1]:
                            print(title)
                    else:
                        longest_streak = get_longest_streak(habit_title)
                        console.print(f'Longest streak for \'{habit_title}\': {str(longest_streak)}', style=info_style)
                # 'Return to main menu' option
                else: 
                    pass  
            else:
                console.print('No habits found', style=cancel_style)
        # 'Exit' option 
        else:
            is_user_ready = False # stop loop
            console.print('Application stopped by user', style=cancel_style)

if __name__ == '__main__':
    run_application()