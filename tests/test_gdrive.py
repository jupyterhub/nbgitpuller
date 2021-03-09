import unittest
from unittest.mock import patch
import unittest.mock
from google_auth_oauthlib.flow import InstalledAppFlow
import io
import os
from googleapiclient.http import MediaIoBaseDownload
from nbgitpuller.plugins import gdrive_commands

class ServiceFilesMock(dict):

    def __init__(self):
        super(ServiceFilesMock, self).__init__()
        fileInfoMock = {'name':'some_name', 'mimeType':'application/vnd.google-apps.folder'}
        self['files'] = [fileInfoMock]
        self.uri = None
        self.headers = None

    def files(self, *args, **kwargs):
        return ServiceFilesMock()

    def list(self, *args, **kwargs):
        return ServiceFilesMock()

    def execute(self, *args, **kwargs):
        return ServiceFilesMock()

    def get_media(self, *args, **kwargs):
        return ServiceFilesMock()

class DownloaderMock():

    def next_chunk(self, *args, **kwargs):
        return (True, True)

class FileHandlerMock():

    def close(self, *args, **kwargs):
        return

class TestPlugin(unittest.TestCase):

    def test_auth(self):
        """Unit test: Checks whether user is redirected to Google auth login."""
        with patch('nbgitpuller.plugins.gdrive_commands.InstalledAppFlow.run_local_server') as mocked:
            mocked.return_value.ok = True
            response = gdrive_commands.auth()
        self.assertIsNotNone(response)

    def test_access_foldercontents(self):
        """Unit test: Checks whether proper API calls made to list all Drive files."""
        service = ServiceFilesMock()
        Folder_id = 'some_file_id'
        response = gdrive_commands.listFiles(service, Folder_id)
        self.assertIsNotNone(response)

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def assert_stdout_download(self, expected_output, mock_stdout):
        service = ServiceFilesMock()
        Folder_id = 'some_file_id'
        with patch('nbgitpuller.plugins.gdrive_commands.os.mkdir') as mocked1:
            mocked1.return_value.ok = True
            with patch('nbgitpuller.plugins.gdrive_commands.io.FileIO') as mocked2:
                mocked2.return_value = FileHandlerMock()
                with patch('nbgitpuller.plugins.gdrive_commands.MediaIoBaseDownload') as mocked3:
                    mocked3.return_value = DownloaderMock()
                    gdrive_commands.download_folder(service, Folder_id)
                    self.assertEqual(mock_stdout.getvalue(), expected_output)

    def test_download_folder(self):
         """Unit test: Check if user is able to download all contents of folder with specified folder id."""
         self.assert_stdout_download('Downloading...some_name\n')
