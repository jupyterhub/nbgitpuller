import nbgitpuller
from git import Repo

 @nbgitpuller.hookimpl
 def sync_file_management_system(repo: str, parent_dir: str, repo_dir: str):
     """
     Checks if the current remote git repository exists from repo.

     Then updates or pulls FMS notebook files into remote repo

     Then checks to see if corresponding local repository exists.

     If first time user, creates local repository for this assignment by pulling
     remote repository into local directory, where student makes changes

     Else, merges remote repository with local repository according to nbgitpuller
     merge conventions
     """

@nbgitpuller.hookimpl
def check_fms(type: str):
    """
    checks to see if current file management system is git or a third party FMS

    Returns True if it is a third party FMS
    Else returns False
    """

@nbgitpuller.hookimpl
def is_new_assignment():
    """
    Checks if current requested repository is a new assignment for current student
    by checking if local repository exists

    If local repo does not exist, return the directory path of the root of the repo
    """

def init_repo(repo_path):
    """Initializes Git Repository at specified directory path. If not possible, throws error."""
    try:
        repository = Repo.init(path=repo_path, bare=False, mkdir=True)
        return repository
    except:
        print('Some error occurred while initializing the repository.')
        return
