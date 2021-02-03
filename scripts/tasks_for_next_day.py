from todoist_habit_tracker.todoist_connection import TodoistConnection
from todoist_habit_tracker.habit import Habit
from datetime import datetime, timedelta
import os
import pandas as pd
import sys, getopt

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

def init_todoist():
    dirname = os.path.abspath(os.path.dirname(__file__))
    filename = os.path.join(os.path.split(dirname)[0], '.config/.todoist.txt')
    todoist = TodoistConnection.from_config_file(filename)
    return todoist

def init_drive(folder):
    gauth = GoogleAuth()
    dirname = os.path.abspath(os.path.abspath(__file__))
    filename = os.path.join(os.path.split(dirname)[0], '../.config/.drive_credentials.json')
    gauth.LoadCredentialsFile(filename)
    if gauth.access_token_expired:
        gauth.Refresh()
    drive = GoogleDrive(gauth)
    folder_id = drive.ListFile(
        {'q': "title='" + folder + "' and mimeType='application/vnd.google-apps.folder' and trashed=false"}).GetList()[
        0]['id']
    return drive, folder_id

def load_data(drive_api, folder_id, filename, fullpath):
    file = drive_api.ListFile({'q': "'{0}' in parents and trashed=false and title = '{1}'".format(folder_id, filename)}).GetList()[0]
    file.GetContentFile(fullpath)
    return pd.read_csv(fullpath, index_col=0), file['id']


def append_data(succes_dict, weekly=False):
    dirname = os.path.abspath(os.path.abspath(__file__))
    filename = os.path.join(os.path.split(dirname)[0], '../log/{0}_tasks.csv'.format(('weekly' if weekly else 'daily')))
    drive_api, folder_id = init_drive('QS')
    df, file_id = load_data(drive_api, folder_id, 'daily_tasks.csv', filename)
    min_days = 7 if weekly else 1
    index = (datetime.today() - timedelta(days=min_days)).strftime('%d/%m/%Y')
    df = df.append(pd.DataFrame(succes_dict, index=[index]))
    df.to_csv(filename)
    file = drive_api.CreateFile({'id': file_id, 'title': 'daily_tasks.csv', 'parents': [{'id': folder_id}]})
    file.SetContentFile(filename)
    file.Upload({'convert': False})


def main(argv):
    test = False
    do_succes = False
    weekly = False
    LABEL = 'habit_automatic'
    WEEKLY_LABEL = 'upcoming_week'
    TEST_PROJECT='habit_tracker_test'
    try:
        opts, args = getopt.getopt(argv, 'ts:w:')
    except getopt.GetoptError:
        sys.exit(2)
    for opt, args in opts:
        if opt == '-t':
            test = True
        if opt == '-s':
            do_succes = args.lower() == 'true'
        if opt == '-w':
            weekly = args.lower() == 'true'
    todoist = init_todoist()
    label_id = todoist.get_label_by_name(LABEL)['id']
    weekly_label_id = todoist.get_label_by_name(WEEKLY_LABEL)['id']
    project_id = todoist.get_project_by_name(TEST_PROJECT)['id']
    if test:
        habits = todoist.filter_tasks(lambda task: (label_id in task['labels']) and (project_id == task['project_id']))
    else:
        habits = todoist.filter_tasks(lambda task: (label_id in task['labels']) and (project_id != task['project_id']))
    habit_objects = [Habit(habit, todoist, label_id, weekly_label_id) for habit in habits]
    habit_objects = filter(lambda habit: habit.weekly, habit_objects) if weekly \
        else filter(lambda habit: habit.daily, habit_objects)
    succes = {}
    for habit in habit_objects:
        succes[str(habit)] = habit.done()
        habit.determine_action()

    # todoist.commit()
    if do_succes:
        print('here')
        append_data(succes)
    return todoist


if __name__ == '__main__':
    main(sys.argv[1:])
