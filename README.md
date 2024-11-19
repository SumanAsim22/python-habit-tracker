# Python Habit Tracker

## Description
This project is a Python application designed to help users track their habits. 
It allows users to create, view, and delete habits, as well as track their streaks and task completions.
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

## Installation and Running
1. Clone the repository
   git clone https://github.com/yourusername/python-habit-tracker.git
2. Navigate to the directory where the project is located
3. Install the dependencies listed in the `requirements.txt` file
   `pip install -r requirements.txt`
4. Start the Habit Tracker application using the following command
   `python main.py`
