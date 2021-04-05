import pickle
import os.path
import os
import io
import json
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseDownload
from oauth2client.service_account import ServiceAccountCredentials


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive']


def listFiles(service, folder_id, return_folder_name=False):
    listOfFiles = []
    query = f"'{folder_id}' in parents'"
    # Get list of jpg files in shared folder
    page_token = None
    results = service.files().list(q = "'{}' in parents".format(folder_id),
        pageSize=10, fields="nextPageToken, files(id, name)").execute()
    folder_name = [fileInfo['name'] for fileInfo in service.files(
    ).list().execute()['files'] if fileInfo['mimeType'] == 'application/vnd.google-apps.folder'][0]
    listOfFiles = [{'id':file.get('id'), 'name':file.get('name')} for file in results['files']]
    if return_folder_name:
        return listOfFiles, folder_name
    else:
        return listOfFiles

# To Download Single File
def download_file(service, file_id):
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print ("Download %d%%." % int(status.progress() * 100))

# To Download Single Folder
def download_folder(service, folder_id):
    listOfFiles, folder_name = listFiles(service, folder_id, return_folder_name=True)
    file_path = os.getcwd()
    file_path += '/{}/'.format(folder_name)
    os.mkdir(file_path)
    for fileID in listOfFiles:
        request = service.files().get_media(fileId=fileID['id'])
        fh = io.FileIO(file_path + fileID['name'], 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print("Downloading..." + str(fileID['name']))
        fh.close()
        # split into separate functions to test each one

def auth():
    """Authenticates user to access Drive files."""
    # Requires JupyterHub
    try:
        json = json.loads(os.environ['DRIVE_CREDS'])
    except KeyError:
        raise KeyError('Drive Credentials not found. Please update DataHub staging with API credentials.')
    drive_creds = ServiceAccountCredentials.from_json_keyfile_dict(json, SCOPES)

    # Open Google Drive authentication portal
    flow = InstalledAppFlow.from_client_secrets_file(
                drive_creds, SCOPES)
    creds = flow.run_local_server()
    return creds
