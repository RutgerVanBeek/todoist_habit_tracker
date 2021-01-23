from todoist_habit_tracker import todoist_connection
import os
from datetime import datetime

if __name__ == '__main__':
    dirname = os.path.abspath(os.path.dirname(__file__))
    filename = os.path.join(os.path.split(dirname)[0], '.config/.todoist.txt')
    todoist = todoist_connection.TodoistConnection.from_config_file(filename)
    dumpfile = os.path.join(os.path.split(dirname)[0], 'log/log.txt')
    print(len(todoist.uncompleted_tasks))
    try:
        with open(dumpfile, 'a') as f:
            f.write(str(datetime.now()) + '     ' + str(len(todoist.uncompleted_tasks)) + '\n')
    except FileNotFoundError:
        with open(dumpfile, 'w') as f:
            f.write(str(datetime.now()) + '     ' + str(len(todoist.uncompleted_tasks)) + '\n')
