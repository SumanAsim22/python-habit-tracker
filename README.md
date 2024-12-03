# Python Habit Tracker

## Description
This project is a Python application designed to help users track their habits. 
It allows users to create, view, and delete habits, as well as track their progress with task checkoffs and streaks.
As of the current version, the application can only be interacted with via the command line.

## Features 
- Add new habits with a title, description, and frequency
- View all habits in a structured table
- Checkoff habit tasks and establish streaks
- Filter habits based on frequency (daily/weekly), streak status (active/inactive), and task checkoff count
- Track and view longest streaks
- Interact with CLI menus and receive clear outputs

## Requirements 
- Python 3.x (includes `sqlite3` and `datetime` modules)
- Questionary
- Rich
- Pytest

## Installation and Running
1. Clone the repository:
   `git clone https://github.com/yourusername/python-habit-tracker.git`
3. Navigate to the directory where the project is located.
4. Install the dependencies listed in the `requirements.txt` file: `pip install -r requirements.txt`
5. Start the Habit Tracker application using the following command: `python main.py`
6. Enter the name of the database to connect to (e.g. `test.db`).

**Note:**
- The project comes with a preexisitng database `test.db`. This database contains 5 predefined habits as well as example task checkoffs for a period of 4 weeks and the corresponding streaks. It can be used to gain an understanding of the application.
- To work with a new database, enter the preferred database name when prompted (e.g. `main.db`). This will create a blank database and connect the application to it. When restarting the application, enter this name again to load the stored data.

## Example usage
- Enter database name and start the application.
- Creating a new habit: 
   -> Select 'Create new habit' from the main menu 
   -> Enter habit details as prompted 
   -> Confirm habit creation
- Checking off a habit: 
   -> Select 'Manage habits' from the main menu 
   -> Select 'Checkoff a habit' from the sub-menu 
   -> Select the required habit to checkoff 
   -> Navigate to 'Manage habits' again to view the changes in the table
**Note:** To maintain a streak, daily habits need to be checked off at least once every day, and weekly habits need to be checked off at least once every week (a week is calculated from each Monday to Sunday). A new streak starts whenever a streak is broken.

## Testing with Pytest
- This project uses pytest for testing. 
- Pytest is installed as part of the project's requirements (see **Installation and Running** - step 4).
- The unit test suite for the project is found in `test_habit_tracker.py`
- To run the test, execute the following command in the project directory: `pytest`