import os
import pytest
import shutil
import nbgitpuller.plugin_helper as ph
import importlib
import aiohttp
from aioresponses import aioresponses
google_nb = importlib.import_module("nbgitpuller.plugins.nbgitpuller-googledrive.googledrive_puller")

test_files_dir = os.getcwd() + "/tests/test_files"
archive_base = "/tmp/test_files"
repo_parent_dir = "/tmp/fake/"
temp_download_repo = "/tmp/download/"
temp_archive_download = "/tmp/archive_download/"
provider = "dropbox_test"
url = "http://test/this/repo"
CACHED_ORIGIN_NON_GIT_REPO = ".nbgitpuller/targets/"
origin_repo = f"{repo_parent_dir}{CACHED_ORIGIN_NON_GIT_REPO}{provider}/{url}/"

repo_zip = 'file://' + archive_base + ".zip"
repo_tgz = 'file://' + archive_base + ".tar.gz"


@pytest.fixture
async def test_configuration():
    shutil.make_archive(archive_base, 'zip', test_files_dir)
    shutil.make_archive(archive_base, 'gztar', test_files_dir)
    os.makedirs(temp_archive_download, exist_ok=True)
    os.makedirs(repo_parent_dir, exist_ok=True)
    os.makedirs(temp_download_repo, exist_ok=True)
    yield "test finishing"
    os.remove(archive_base + ".zip")
    os.remove(archive_base + ".tar.gz")
    if os.path.isfile(temp_archive_download + "downloaded.zip"):
        os.remove(temp_archive_download + "downloaded.zip")
    shutil.rmtree(repo_parent_dir)
    shutil.rmtree(temp_download_repo)
    shutil.rmtree(temp_archive_download)


def test_extract_file_extension():
    url = "https://example.org/master/materials-sp20-external.tgz"
    ext = ph.extract_file_extension(url)
    assert "tgz" in ext


@pytest.mark.asyncio
async def test_initialize_local_repo(test_configuration):
    yield_str = ""
    async for line in ph.initialize_local_repo(origin_repo):
        yield_str += line
    assert "init --bare" in yield_str
    assert os.path.isdir(origin_repo)


@pytest.mark.asyncio
async def test_clone_local_origin_repo(test_configuration):
    async for line in ph.initialize_local_repo(origin_repo):
        pass

    yield_str = ""
    async for line in ph.clone_local_origin_repo(origin_repo, temp_download_repo):
        yield_str += line

    assert "Cloning into" in yield_str
    assert os.path.isdir(temp_download_repo + ".git")


@pytest.mark.asyncio
async def test_execute_unarchive(test_configuration):
    yield_str = ""
    async for line in ph.execute_unarchive("zip", archive_base + ".zip", temp_download_repo):
        yield_str += line
    assert os.path.isfile("/tmp/download/test.txt")


@pytest.mark.asyncio
async def test_push_to_local_origin(test_configuration):
    async for line in ph.initialize_local_repo(origin_repo):
        pass

    async for line in ph.clone_local_origin_repo(origin_repo, temp_download_repo):
        pass

    async for line in ph.execute_unarchive("zip", archive_base + ".zip", temp_download_repo):
        pass

    yield_str = ""
    async for line in ph.push_to_local_origin(temp_download_repo):
        yield_str += line
    assert "[new branch]" in yield_str


@pytest.mark.asyncio
async def test_download_archive(test_configuration):
    args = {}
    args["repo"] = "http://fake.com"
    with aioresponses() as mocked:
        mocked.get(args["repo"], status=200, body=b'Pretend you are zip file being downloaded')
        args["client"] = aiohttp.ClientSession()
        yield_str = ""
        async for line in ph.download_archive(args, temp_archive_download + "downloaded.zip"):
            yield_str += line
    assert 'Downloading archive' in yield_str
    assert os.path.isfile(temp_archive_download + "downloaded.zip")


def test_google_get_id():
    google_repo = "https://drive.google.com/fake/d/1111122223333444444/view?usp=sharing"
    gnb = getattr(google_nb, "get_id")
    file_id = gnb(google_repo)
    assert file_id == "1111122223333444444"
