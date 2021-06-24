import os
import pytest
import shutil
from nbgitpuller.plugins.zip_puller import ZipSourceWebDownloader
from nbgitpuller.plugins.zip_puller import ZipSourceDropBoxDownloader
from nbgitpuller.plugins.zip_puller import ZipSourceGoogleDriveDownloader

test_files_dir = os.getcwd() + "/tests/test_files"
archive_base = "/tmp/test_files"
repo_parent_dir = "/tmp/fake/"
repo_zip = 'file://' + archive_base + ".zip"
repo_tgz = 'file://' + archive_base + ".tar.gz"


@pytest.fixture
def test_configuration():
    shutil.make_archive(archive_base, 'zip', test_files_dir)
    shutil.make_archive(archive_base, 'gztar', test_files_dir)
    os.makedirs(repo_parent_dir, exist_ok=True)
    yield "test finishing"
    shutil.rmtree(repo_parent_dir)
    os.remove(archive_base + ".zip")
    os.remove(archive_base + ".tar.gz")


def assert_helper(down, zip, tgz):
    resp_zip = down.handle_files(zip, repo_parent_dir)
    resp_tgz = down.handle_files(tgz, repo_parent_dir)
    assert "unzip_dir" in resp_zip
    assert "origin_repo_path" in resp_zip
    assert f"{repo_parent_dir}.origin_non_git_sources" in resp_zip["origin_repo_path"]
    assert "hw" in resp_zip["unzip_dir"]
    assert "unzip_dir" in resp_tgz
    assert "origin_repo_path" in resp_tgz
    assert f"{repo_parent_dir}.origin_non_git_sources" in resp_tgz["origin_repo_path"]
    assert "hw" in resp_tgz["unzip_dir"]


def test_web_downloader(test_configuration):
    down = ZipSourceWebDownloader()
    assert_helper(down, repo_zip, repo_tgz)


def test_dropbox_downloader(test_configuration):
    down = ZipSourceDropBoxDownloader()
    drop_repo_zip = repo_zip + "?dl=0"
    drop_repo_tgz = repo_tgz + "?dl=0"
    assert_helper(down, drop_repo_zip, drop_repo_tgz)


def test_google_get_id():
    down = ZipSourceGoogleDriveDownloader()
    google_repo = "https://drive.google.com/file/d/1p3m0h5UGWdLkVVP0SSJH6j1HpG2yeDlU/view?usp=sharing"
    file_id = down.get_id(google_repo)
    assert file_id == "1p3m0h5UGWdLkVVP0SSJH6j1HpG2yeDlU"
