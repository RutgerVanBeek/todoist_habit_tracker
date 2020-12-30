from todoist_habit_tracker.todoist_connection import TodoistConnection
from todoist_habit_tracker.habit import Habit
import os
from datetime import datetime
PROJECT = 'habit_tracker_test'
LABEL = 'habit'



def init_todoist():
    dirname = os.path.abspath(os.path.dirname(__file__))
    filename = os.path.join(os.path.split(dirname)[0], '.config/.todoist.txt')
    print(filename)
    todoist = TodoistConnection.from_config_file(filename)
    return todoist


def main():
    LABEL = 'habit'
    print('start')
    todoist = init_todoist()
    # todoist = TodoistConnection.from_config_file(config_file)
    print('initialized')
    # project_id = list(filter(lambda project: project['name'] == PROJECT, todoist.projects))[-1]['id']
    label_id = todoist.get_label_by_name(LABEL)['id']
    habits = todoist.filter_tasks(lambda task: label_id in task['labels'])
    print(len(habits))
    habit_objects = [Habit(habit, todoist, label_id) for habit in habits]
    for habit in habit_objects:
        print(habit)
        habit.determine_action()
    print('created tasks')
    todoist.commit()
    print('commited')
    return todoist


if __name__ == '__main__':
    main()