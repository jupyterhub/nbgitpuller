import nbgitpuller
from git import Repo

from __future__ import print_function
import pickle
import os
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from apiclient.http import MediaFileUpload, MediaIoBaseDownload
import io
from apiclient import errors
from apiclient import http
import logging

from apiclient import discovery

SCOPES = ['https://www.googleapis.com/auth/drive']

 @nbgitpuller.hookimpl
 def sync_file_management_system(repo: str, parent_dir: str, repo_dir: str):
     """
     Checks if the current remote googleDrive repository exists from 'repo'.

     Then checks to see if corresponding local repository exists.

     If first time user, creates local repository for this assignment by pulling
     remote repository into local directory, where student makes changes

     Else, merges remote repository with local repository according to nbgitpuller
     merge conventions
     """

     try:
         is_new = is_new_assignment(parent_dir, repo_dir)
     except:
         print('Some error occurred while initializing the repository.')
         return

    if is_new:
        init_repo(repo)

    service = user_auth()
    check_and_download(parent_dir, repo_dir)





def user_auth():
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

    service = build('drive', 'v3', credentials=creds)

    return service



# @nbgitpuller.hookimpl
# def check_fms(type: str):
#     """
#     checks to see if current file management system is git or a third party FMS
#
#     Returns True if it is a third party FMS
#     Else returns False
#     """

# def find_download(parent_dir, repo_dir):
#     file_id = '1yrRDlhH2LwWXjezh2_0aqIYHT3XQ-MXN'
#
#
#
#
    # page_token = None
    # while True:
    #     response = service.files().list(q="mimeType='application/vnd.google-apps.folder'",
    #                                           spaces='drive',
    #                                           fields='nextPageToken, files(id, name)',
    #                                           pageToken=page_token).execute()
    #     for file in response.get('files', []):
    #         # Process change
    #         print('Found file: %s (%s)' % (file.get('name'), file.get('id')))
    #     page_token = response.get('nextPageToken', None)
    #     if page_token is None:
    #         break
    #
    #
    #
    #
    #
    #
    # request = service.files().get_media(fileId=file_id)
    # fh = io.BytesIO()
    # downloader = MediaIoBaseDownload(fh, request)
    # done = False
    # while done is False:
    #     status, done = downloader.next_chunk()
    #     print("Download %d%%." % int(status.progress() * 100))
    #
    # fh.seek(0)
    #
    # file_name = "init.py" # get_name(file_id)
    #
    # # path = os.path.join('./RandoFile', file_name)
    # #
    # # # Create the directory
    # # # 'GeeksForGeeks' in
    # # # '/home / User / Documents'
    # # os.makedirs(path)
    # print('open is assigned to %r' % open)
    #
    # with open(os.path.join('./RandoFile', file_name), 'wb') as f:
    #     f.write(fh.read())
    #     f.close()


def check_and_download(parent_dir, repo_dir):
    # Folder_id = get_id_from_repo(repo_dir)
    Folder_id = "'1HONxE6lCjgQA7Djko3UIzAdbfM_2RHIT'"  # Enter The Downloadable folder ID From Shared Link
    fid = '1HONxE6lCjgQA7Djko3UIzAdbfM_2RHIT'
    page_token = None
    results = service.files().list(pageSize=1000, q=Folder_id+" in parents", fields="nextPageToken, files(id, name, mimeType)").execute()


    items = results.get('files', [])
    if not items:
        print('No files found.')
    else:
        print('Files:')
        print(items)
        for item in items:
            if item['mimeType'] == 'application/vnd.google-apps.folder':
                if not os.path.isdir(fid):
                    os.mkdir(fid)
                bfolderpath = os.getcwd()+ "/" + fid + "/"
                if not os.path.isdir(bfolderpath + item['name']):
                    os.mkdir(bfolderpath + item['name'])

                folderpath = bfolderpath + item['name']
                listfolders(service, item['id'], folderpath)
            else:
                if not os.path.isdir(fid):
                    os.mkdir(fid)
                bfolderpath = os.getcwd() + "/" + fid + "/"
                if not os.path.isdir(bfolderpath + item['name']):
                    os.mkdir(bfolderpath + item['name'])

                filepath = bfolderpath + item['name']
                downloadfiles(service, item['id'], item['name'], filepath)
        repo = git.Repo(fid, search_parent_directories=True)
        commit_repo(repo)


        

# To list folders
def listfolders(service, filid, des):
    results = service.files().list(
        pageSize=1000, q="\'" + filid + "\'" + " in parents",
        fields="nextPageToken, files(id, name, mimeType)").execute()
    # logging.debug(folder)
    folder = results.get('files', [])
    for item in folder:
        if str(item['mimeType']) == str('application/vnd.google-apps.folder'):
            if not os.path.isdir(des+"/"+item['name']):
                os.mkdir(path=des+"/"+item['name'])
            print(item['name'])
            listfolders(service, item['id'], des+"/"+item['name'])  # LOOP un-till the files are found
        else:
            downloadfiles(service, item['id'], item['name'], des)
            print(item['name'])
    return folder


# To Download Files
def downloadfiles(service, dowid, name,dfilespath):
    request = service.files().get_media(fileId=dowid)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print("Download %d%%." % int(status.progress() * 100))
    with io.open(dfilespath + "/" + name, 'wb') as f:
        fh.seek(0)
        f.write(fh.read())



@nbgitpuller.hookimpl
def is_new_assignment(path):
    """
    Checks if current requested repository is a new assignment for current student
    by checking if local repository exists

    If local repo does not exist, return the directory path of the root of the repo
    """
    isFile = os.path.isfile(path)
    return os.path.isdir(path)




def init_repo(repo_path):
    """Initializes Git Repository at specified directory path. If not possible, throws error."""
    #convert
    try:
        repository = Repo.init(path=repo_path, bare=False, mkdir=True)
        repository.git.commit('-m', 'initial commit')
        return repository
    except:
        print('Some error occurred while initializing the repository.')
        return

def commit_repo(repo):
    repo.git.commit('-m', 'pulled from drive')
