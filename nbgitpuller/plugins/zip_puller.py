from .plugin_helper import fetch_files
from .plugin_helper import handle_files_helper
import pluggy

hookimpl = pluggy.HookimplMarker("nbgitpuller")
TEMP_DOWNLOAD_REPO_DIR = ".temp_download_repo"
CACHED_ORIGIN_NON_GIT_REPO = ".origin_non_git_sources"


# handles standard web addresses(not google drive or dropbox)
class ZipSourceWebDownloader(object):
    @hookimpl
    def handle_files(self, repo, repo_parent_dir):
        """
        :param str repo: publicly accessible url to compressed source files
        :param str repo_parent_dir: where we will store the downloaded repo
        :return two parameter json unzip_dir and origin_repo_path
        :rtype json object
        """
        response = fetch_files(repo)
        args = {
            "repo": repo,
            "repo_parent_dir": repo_parent_dir,
            "response": response,
            "origin_dir": CACHED_ORIGIN_NON_GIT_REPO,
            "download_dir": TEMP_DOWNLOAD_REPO_DIR
        }
        return handle_files_helper(args)


# handles downloads from google drive
class ZipSourceGoogleDriveDownloader(object):
    def __init__(self):
        self.DOWNLOAD_URL = "https://docs.google.com/uc?export=download"

    def get_id(self, repo):
        start_id_index = repo.index("d/") + 2
        end_id_index = repo.index("/view")
        return repo[start_id_index:end_id_index]

    @hookimpl
    def handle_files(self, repo, repo_parent_dir):
        """
        :param str repo: google drive share link to compressed source files
        :param str repo_parent_dir: where we will store the downloaded repo
        :return two parameter json unzip_dir and origin_repo_path
        :rtype json object
        """
        response = fetch_files(self.DOWNLOAD_URL, self.get_id(repo))
        args = {
            "repo": repo,
            "repo_parent_dir": repo_parent_dir,
            "response": response,
            "origin_dir": CACHED_ORIGIN_NON_GIT_REPO,
            "download_dir": TEMP_DOWNLOAD_REPO_DIR
        }
        return handle_files_helper(args)


# handles downloads from DropBox
class ZipSourceDropBoxDownloader(object):
    @hookimpl
    def handle_files(self, repo, repo_parent_dir):
        """
        :param str repo: dropbox download link to compressed source files
        :param str repo_parent_dir: where we will store the downloaded repo
        :return two parameter json unzip_dir and origin_repo_path
        :rtype json object
        """
        repo = repo.replace("dl=0", "dl=1")  # download set to 1 for dropbox
        response = fetch_files(repo)
        args = {
            "repo": repo,
            "repo_parent_dir": repo_parent_dir,
            "response": response,
            "origin_dir": CACHED_ORIGIN_NON_GIT_REPO,
            "download_dir": TEMP_DOWNLOAD_REPO_DIR
        }
        return handle_files_helper(args)
