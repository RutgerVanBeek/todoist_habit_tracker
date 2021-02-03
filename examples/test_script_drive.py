import pydrive
import pandas as pd
from datetime import datetime
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os

def main():
    gauth = GoogleAuth()
    dirname = os.path.abspath(os.path.abspath(__file__))
    filename = os.path.join(os.path.split(dirname)[0], '../.config/.drive_credentials.json')
    print(filename)
    gauth.LoadCredentialsFile(filename)
    # gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)
    # create random pandas dataframe
    test_df = pd.DataFrame({'a':[datetime.now(),2],'b':[2,3]})
    #upload to QS
    df_to_drive('QS', drive, test_df, 'test.csv')


def df_to_drive(folder, drive_api, df, title):
    folder_id = drive_api.ListFile({'q': "title='" + folder + "' and mimeType='application/vnd.google-apps.folder' and trashed=false"}).GetList()[0]['id']
    f = drive_api.CreateFile({'title': title, 'parents': [{'id': folder_id}]})
    dirname = os.path.abspath(os.path.abspath(__file__))
    filename = os.path.join(os.path.split(dirname)[0], '../log/{0}.csv'.format(title))
    df.to_csv(filename)
    f.SetContentFile(filename)
    f.Upload({'convert': True})

if __name__ == '__main__':
    main()