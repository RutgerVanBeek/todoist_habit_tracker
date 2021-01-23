from todoist_habit_tracker.todoist_connection import TodoistConnection
from todoist_habit_tracker.habit import Habit
import os
from datetime import datetime

def init_todoist():
    dirname = os.path.abspath(os.path.dirname(__file__))
    filename = os.path.join(os.path.split(dirname)[0], '.config/.todoist.txt')
    todoist = TodoistConnection.from_config_file(filename)
    return todoist


def main():
    LABEL = 'habit_automatic'
    todoist = init_todoist()
    label_id = todoist.get_label_by_name(LABEL)['id']
    habits = todoist.filter_tasks(lambda task: label_id in task['labels'])
    habit_objects = [Habit(habit, todoist, label_id) for habit in habits]
    for habit in habit_objects:
        habit.determine_action()
    todoist.commit()
    return todoist


if __name__ == '__main__':
    main()