from todoist_habit_tracker.todoist_connection import TodoistConnection
from todoist_habit_tracker.habit import Habit
from datetime import datetime, timedelta
import os
import pandas as pd
import sys
import getopt

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
    folder_id = drive.ListFile({'q': "title='" + folder + "' and mimeType='application/vnd.google-apps.folder' and "
                                                          "trashed=false"}).GetList()[0]['id']
    return drive, folder_id


def load_data(drive_api, folder_id, filename, fullpath):
    file = drive_api.ListFile({'q': "'{0}' in parents and trashed=false and title = '{1}'".format(folder_id, filename)
                               }).GetList()[0]
    file.GetContentFile(fullpath)
    return pd.read_csv(fullpath, index_col=0), file['id']


def append_data(succes_dict):
    dirname = os.path.abspath(os.path.abspath(__file__))
    filename = os.path.join(os.path.split(dirname)[0], '../log/daily_tasks.csv')
    drive_api, folder_id = init_drive('QS')
    df, file_id = load_data(drive_api, folder_id, 'daily_tasks.csv', filename)
    index = (datetime.today() - timedelta(days=1)).strftime('%d/%m/%Y')
    df = df.append(pd.DataFrame(succes_dict, index=[index]))
    df.to_csv(filename)
    file = drive_api.CreateFile({'id': file_id, 'title': 'daily_tasks.csv', 'parents': [{'id': folder_id}]})
    file.SetContentFile(filename)
    file.Upload({'convert': False})


def main(argv):
    test = False
    do_succes = False
    LABEL = 'habit_automatic'
    TEST_PROJECT = 'habit_tracker_test'
    try:
        opts, args = getopt.getopt(argv, 'ts:')
    except getopt.GetoptError:
        sys.exit(2)
    for opt, args in opts:
        if opt == '-t':
            test = True
        if opt == '-s':
            do_succes = args.lower() == 'true'
    todoist = init_todoist()
    label_id = todoist.get_label_by_name(LABEL)['id']
    project_id = todoist.get_project_by_name(TEST_PROJECT)['id']
    habits = todoist.filter_tasks(lambda task: (label_id in task['labels']) and
                                               (test == (project_id == task['project_id'])))
    habit_objects = [Habit(habit, todoist, label_id) for habit in habits]
    succes = {}
    for habit in habit_objects:
        succes[str(habit)] = habit.done()
        habit.determine_action()

    todoist.commit()
    if do_succes:
        append_data(succes)
    return todoist


if __name__ == '__main__':
    main(sys.argv[1:])
