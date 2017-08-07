import os
import re
import subprocess
import logging
import argparse


class GitAutoSync:
    DELETED_FILE_REGEX = re.compile(
        r"deleted:\s+"  # Look for deleted: + any amount of whitespace...
        r"([^\n\r]+)"   # and match the filename afterward.
    )

    MODIFIED_FILE_REGEX = re.compile(
        r"^\s*M\s+(.*)$",  # Look for M surrounded by whitespaeces and match filename afterward
        re.MULTILINE
    )

    def __init__(self, git_url, branch_name, repo_dir):
        assert git_url and branch_name

        self._git_url = git_url
        self._branch_name = branch_name
        self._repo_dir = repo_dir

    def pull_from_remote(self):
        """
        Pull selected repo from a remote git repository,
        while preserving user changes
        """

        logging.info('Pulling into {} from {}, branch {}'.format(
            self._repo_dir,
            self._git_url,
            self._branch_name
        ))

        if not os.path.exists(self._repo_dir):
            self._initialize_repo()
        else:
            self._update_repo()

        logging.info('Pulled from repo: {}'.format(self._git_url))

    def _initialize_repo(self):
        """
        Clones repository.
        """

        logging.info('Repo {} doesn\'t exist. Cloning...'.format(self._repo_dir))
        subprocess.check_call(['git', 'clone', self._git_url, self._repo_dir])
        logging.info('Repo {} initialized'.format(self._repo_dir))

    def _update_repo(self):
        """
        Update repo by merging local and upstream changes
        """

        self._reset_deleted_files()
        if self.repo_is_dirty():
            self._make_commit()
        self._pull_and_resolve_conflicts()

    def _reset_deleted_files(self):
        """
        Runs the equivalent of git checkout -- <file> for each file that was
        deleted. This allows us to delete a file, hit an interact link, then get a
        clean version of the file again.
        """

        status = subprocess.check_output(['git', 'status'], cwd=self._repo_dir)
        deleted_files = self.DELETED_FILE_REGEX.findall(status.decode('utf-8'))

        for filename in deleted_files:
            subprocess.check_call(['git', 'checkout', '--', filename], cwd=self._repo_dir)
            logging.info('Resetted {}'.format(filename))

    def _make_commit(self):
        """
        Commit local changes
        """

        subprocess.check_call(['git', 'checkout', self._branch_name], cwd=self._repo_dir)
        subprocess.check_call(['git', 'add', '-A'], cwd=self._repo_dir)
        subprocess.check_call(['git', 'config', 'user.email', '"gitautopull@email.com"'], cwd=self._repo_dir)
        subprocess.check_call(['git', 'config', 'user.name', '"GitAutoPull"'], cwd=self._repo_dir)
        subprocess.check_call(['git', 'commit', '-m', 'WIP'], cwd=self._repo_dir)
        logging.info('Made WIP commit')

    def _pull_and_resolve_conflicts(self):
        """
        Git pulls, resolving conflicts with -Xours
        """

        logging.info('Starting pull from {}'.format(self._git_url))

        subprocess.check_call(['git', 'checkout', self._branch_name], cwd=self._repo_dir)
        subprocess.check_call(['git', 'fetch'], cwd=self._repo_dir)
        subprocess.check_call(['git', 'merge', '-Xours', 'origin/{}'.format(self._branch_name)], cwd=self._repo_dir)

        logging.info('Pulled from {}'.format(self._git_url))

    def repo_is_dirty(self):
        """
        Return true if repo is dirty
        """
        output = subprocess.check_output(['git', 'status', '--porcelain'], cwd=self._repo_dir)

        return self.MODIFIED_FILE_REGEX.search(output.decode('utf-8')) is not None


def main():
    """
    Synchronizes a github repository with a local repository.
    Automatically deals with conflicts and produces useful output to stdout.
    """
    logging.basicConfig(
        format='[%(asctime)s] %(levelname)s -- %(message)s',
        level=logging.DEBUG)

    parser = argparse.ArgumentParser(description='Synchronizes a github repository with a local repository.')
    parser.add_argument('--git-url', help='Url of the repo to sync', required=True)
    parser.add_argument('--branch-name', default='master', help='Branch of repo to sync')
    parser.add_argument('--repo-dir', default='./', help='Path to sync to')
    args = parser.parse_args()

    GitAutoSync(
        args.git_url,
        args.branch_name,
        args.repo_dir
    ).pull_from_remote()
