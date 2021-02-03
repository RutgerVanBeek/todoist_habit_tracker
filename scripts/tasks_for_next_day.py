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

def append_data(succes_dict, weekly=False):
    dirname = os.path.abspath(os.path.abspath(__file__))
    filename = os.path.join(os.path.split(dirname)[0], '../log/{0}_tasks.csv'.format(('weekly' if weekly else 'daily')))
    min_days = 7 if weekly else 1
    index = (datetime.today() - timedelta(days=min_days)).strftime('%d/%m/%Y')
    try:
        df = pd.read_csv(filename, index_col=0)
        df = df.append(pd.DataFrame(succes_dict, index=[index]))
    except FileNotFoundError:
        df = pd.DataFrame(succes_dict, index=[index])
    df.to_csv(filename)

def df_to_drive(folder, drive_api, df, title):
    gauth = GoogleAuth()
    dirname = os.path.abspath(os.path.abspath(__file__))
    filename = os.path.join(os.path.split(dirname)[0], '../.config/.drive_credentials.json')
    print(filename)
    gauth.LoadCredentialsFile(filename)
    if gauth.access_token_expired:
        gauth.Refresh()
    drive = GoogleDrive(gauth)
    test_df = pd.DataFrame({'a': [datetime.now(), 2], 'b': [2, 3]})
    df_to_drive('QS', drive, test_df, 'test.csv')
    folder_id = drive_api.ListFile({'q': "title='" + folder + "' and mimeType='application/vnd.google-apps.folder' and trashed=false"}).GetList()[0]['id']
    f = drive_api.CreateFile({'title': title, 'parents': [{'id': folder_id}]})
    dirname = os.path.abspath(os.path.abspath(__file__))
    filename = os.path.join(os.path.split(dirname)[0], '../log/{0}.csv'.format(title))
    df.to_csv(filename)
    f.SetContentFile(filename)
    f.Upload({'convert': True})


def main(argv):
    test = False
    do_succes = False
    weekly = False
    LABEL = 'habit_automatic'
    WEEKLY_LABEL = 'upcoming_week'
    TEST_PROJECT='habit_tracker_test'
    try:
        opts, args = getopt.getopt(argv, 'tsw:')
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

    todoist.commit()
    if do_succes:
        append_data(succes)
    return todoist


if __name__ == '__main__':
    main(sys.argv[1:])
