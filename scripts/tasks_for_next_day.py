from todoist_habit_tracker import todoist_connection
import os
from datetime import datetime
PROJECT = 'habit_tracker_test'
LABEL = 'habit'



def init_todoist():
    dirname = os.path.abspath(os.path.dirname(__file__))
    filename = os.path.join(os.path.split(dirname)[0], '.config/.todoist.txt')
    todoist = todoist_connection.TodoistConnection.from_config_file(filename)
    return todoist


def create_task(habit, label_id):
    # task for the next day with the same id?
    task = {'content': habit['content'], 'project_id': habit['project_id'], 'priority': habit['priority']}
    task['labels'] = [label for label in habit['labels'] if label != label_id]
    task['due'] = {'string': 'tomorrow'}
    return task

def main():
    LABEL = 'habit'
    print('start')
    todoist = init_todoist()
    # todoist = TodoistConnection.from_config_file(config_file)
    print('initialized')
    # project_id = list(filter(lambda project: project['name'] == PROJECT, todoist.projects))[-1]['id']
    label_id = todoist.get_label_by_name(LABEL)['id']
    habits = todoist.filter_tasks(lambda task: label_id in task['labels'])

    for habit in habits:
        # if habit already exists update
        is_equal = lambda task: task['content'] == habit['content'] and task['project_id'] == habit['project_id'] and label_id not in task['labels']
        similar_task = todoist.filter_tasks(is_equal)
        if len(similar_task) > 0:
            similar_task[0].update(due={'string':'today'})
        else:
            todoist.add_task(create_task(habit, label_id))
    print('created tasks')
    todoist.commit()
    print('commited')
    return todoist


if __name__ == '__main__':
    main()