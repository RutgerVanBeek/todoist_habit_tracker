from todoist_habit_tracker import todoist_connection
import os
if __name__ == '__main__':
    dirname = os.path.abspath(os.path.dirname(__file__))
    print(dirname)
    filename = os.path.join(os.path.split(dirname)[0], '.config/.todoist.txt')
    print(filename)
    todoist = todoist_connection.TodoistConnection.from_config_file(filename)
    print(len(todoist.uncompleted_tasks()))