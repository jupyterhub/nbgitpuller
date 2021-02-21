import pickle
import os.path
import os
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import io
from googleapiclient.http import MediaIoBaseDownload

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive']

# To Download Files
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

def download_file(service, file_id):
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print ("Download %d%%." % int(status.progress() * 100))

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

def auth():
    """Authenticates user to access Drive files."""
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)  # credentials.json download from drive API
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds
