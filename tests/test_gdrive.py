import pytest
from unittest import TestCase
import os
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import io
from googleapiclient.http import MediaIoBaseDownload
import unittest
from nbgitpuller.plugins import gdrive_commands
import warnings

class TestPlugin(unittest.TestCase):
    def setUp(self):
        warnings.simplefilter('ignore', category=ImportWarning)

    # def test_auth(self):
    #     """Unit test: Check whether user is able to authenticate and successfully.
    #     User must authenticate every time a download occurs."""
    #     creds = gdrive_commands.auth()
    #     if creds:
    #         assert True
    #     else:
    #         assert False

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

    def test_download_folder(self):
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
        os.remove(file_path + 'test.txt')
        os.remove(file_path + 'requirements.txt')
        os.rmdir(file_path)
