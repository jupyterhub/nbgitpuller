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
import gdrive_commands as drive
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

    # User directed to log into Google
    creds = drive.auth()
    service = build('drive', 'v3', credentials=creds)
    check_and_download(service, parent_dir, repo_dir)

def get_id_from_repo(repo_dir):
    """Returns the Google Drive File/Folder ID for specified files."""
    return repo_dir.split('/')[-1]

def check_and_download(service, parent_dir, repo_dir):
    Folder_id = get_id_from_repo(repo_dir)
    drive.download_folder(service, Folder_id)
    repo = git.Repo(Folder_id, search_parent_directories=True)
    commit_repo(repo)

@nbgitpuller.hookimpl
def is_new_assignment(path):
    """
    Checks if current requested repository is a new assignment for current student
    by checking if local repository exists

    If local repo does not exist, return the directory path of the root of the repo
    """
    isDir = os.path.isdir(path)
    return isDir

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
