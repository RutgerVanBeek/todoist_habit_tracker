from todoist_habit_tracker.todoist_connection import TodoistConnection
from todoist_habit_tracker.habit import Habit
import os
import pandas as pd
import sys, getopt

def init_todoist():
    dirname = os.path.abspath(os.path.dirname(__file__))
    filename = os.path.join(os.path.split(dirname)[0], '.config/.todoist.txt')
    todoist = TodoistConnection.from_config_file(filename)
    return todoist

def open_data():
    dirname = os.path.abspath(os.path.dirname(__file__))
    filename = os.path.join(os.path.split(dirname)[0], '.log/daily_tasks.csv')
    try:
        df = pd.csv_read(filename)
    except FileNotFoundError:
        return pd.DataFrame()



def main(argv):
    test = False
    LABEL = 'habit_automatic'
    TEST_PROJECT='habit_tracker_test'
    try:
        opts, args = getopt.getopt(argv, 't')
    except getopt.GetoptError:
        sys.exit(2)
    for opt, args in opts:
        if opt == '-t':
            test = True
    todoist = init_todoist()
    label_id = todoist.get_label_by_name(LABEL)['id']
    if test:
        project_id = todoist.get_project_by_name(TEST_PROJECT)['id']
        habits = todoist.filter_tasks(lambda task: (label_id in task['labels']) and (project_id == task['project_id']))
    else:
        habits = todoist.filter_tasks(lambda task: label_id in task['labels'])
    habit_objects = [Habit(habit, todoist, label_id) for habit in habits]
    succes = {}
    for habit in habit_objects:
        succes[str(habit)] =  habit.done_yesterday()
        habit.determine_action()

    print(succes)
    todoist.commit()
    return todoist


if __name__ == '__main__':
    main(sys.argv[1:])
