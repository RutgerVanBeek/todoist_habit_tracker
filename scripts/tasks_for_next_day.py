from todoist_habit_tracker import todoist_connection
import os
from datetime import datetime
PROJECT = 'habit_tracker_test'



def init_todoist():
    dirname = os.path.abspath(os.path.dirname(__file__))
    filename = os.path.join(os.path.split(dirname)[0], '.config/.todoist.txt')
    todoist = todoist_connection.TodoistConnection.from_config_file(filename)
    return todoist

def create_task(habit):
    # task for the next day with the same id?




def main():
    todoist = init_todoist()
    project_id = list(filter(lambda project: project['name'] == PROJECT, todoist.projects))[-1]['id']
    habits = todoist.filter_tasks(lambda item: item['project_id'] == project_id)
    [create_task(habit) for habit in habits]



if __name__ == '__main__':
    main()