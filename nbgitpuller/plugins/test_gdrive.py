from __future__ import print_function
import pytest
from unittest import TestCase
import pickle
import os
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import io
from googleapiclient.http import MediaIoBaseDownload
import gdrive_commands

# def test_auth():
#     """Unit test: Check whether user is able to authenticate and successfully:
#     1) If user has previously authenticated, then login should occur automatically and test passes immediately
#     2) If user has not previously authenticated, then login should proceed to Google login page before passing
#     """
#     gdrive_commands.auth()
#     assert os.path.exists('token.pickle')
#     os.remove('token.pickle')

# def test_access_foldercontents():
#     """Unit test: Check if user is able to access folder contents after authenticating"""
#     creds = gdrive_commands.auth()
#     service = build('drive', 'v3', credentials=creds)
#     Folder_id = '1e1SmgYxIJP_3olgkrS7lkqOPnCvhDKmr'
#     item_name = 'nbpuller.gif'
#     item_id = '1J8bUvIrrkPHpley-L6Hu6RrMEAmq-s94'
#     expected_dict = {'id':item_id, 'name':item_name}
#     actual_dict = gdrive_commands.list_files(service, Folder_id)
#     TestCase().assertDictEqual(expected_dict, actual_dict)
#     os.remove('token.pickle')

def test_download_folder():
    """Unit test: Check if user is able to download all contents of folder with specified folder id."""
    creds = gdrive_commands.auth()
    service = build('drive', 'v3', credentials=creds, cache_discovery=False)
    Folder_id = '1e1SmgYxIJP_3olgkrS7lkqOPnCvhDKmr'
    gdrive_commands.download_folder(service, Folder_id)
    file_path = os.getcwd()
    file_path += '/{}/'.format('test-download/')
    assert os.path.isdir(file_path)
    assert os.path.isfile(file_path + 'test.txt')
    assert os.path.isfile(file_path + 'requirements.txt')
    os.remove('token.pickle')
    os.remove(file_path + 'test.txt')
    os.remove(file_path + 'requirements.txt')
    os.rmdir(file_path)
