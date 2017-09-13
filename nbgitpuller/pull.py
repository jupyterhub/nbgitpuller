import os
import re
import subprocess
import logging
import argparse
from functools import partial

def execute_cmd(cmd, **kwargs):
    """
    Call given command, yielding output line by line
    """
    yield '$ {}\n'.format(' '.join(cmd))
    kwargs['stdout'] = subprocess.PIPE
    kwargs['stderr'] = subprocess.STDOUT

    proc = subprocess.Popen(cmd, **kwargs)

    # Capture output for logging.
    # Each line will be yielded as text.
    # This should behave the same as .readline(), but splits on `\r` OR `\n`,
    # not just `\n`.
    buf = []
    def flush():
        line = b''.join(buf).decode('utf8', 'replace')
        buf[:] = []
        return line

    c_last = ''
    try:
        for c in iter(partial(proc.stdout.read, 1), b''):
            if c_last == b'\r' and buf and c != b'\n':
                yield flush()
            buf.append(c)
            if c == b'\n':
                yield flush()
            c_last = c
    finally:
        ret = proc.wait()
        if ret != 0:
            raise subprocess.CalledProcessError(ret, cmd)

class GitPuller:
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

        self.git_url = git_url
        self.branch_name = branch_name
        self.repo_dir = repo_dir

    def pull_from_remote(self):
        """
        Pull selected repo from a remote git repository,
        while preserving user changes
        """

        logging.info('Pulling into {} from {}, branch {}'.format(
            self.repo_dir,
            self.git_url,
            self.branch_name
        ))

        if not os.path.exists(self.repo_dir):
            yield from self._initialize_repo()
        else:
            yield from self._update_repo()

        logging.info('Pulled from repo: {}'.format(self.git_url))

    def _initialize_repo(self):
        """
        Clones repository.
        """

        logging.info('Repo {} doesn\'t exist. Cloning...'.format(self.repo_dir))
        yield from execute_cmd(['git', 'clone', self.git_url, self.repo_dir])
        yield from execute_cmd(['git', 'checkout', self.branch_name], cwd=self.repo_dir)
        logging.info('Repo {} initialized'.format(self.repo_dir))

    def _update_repo(self):
        """
        Update repo by merging local and upstream changes
        """

        yield from self._reset_deleted_files()
        if self.repo_is_dirty():
            yield from self._make_commit()
        yield from self._pull_and_resolve_conflicts()

    def _reset_deleted_files(self):
        """
        Runs the equivalent of git checkout -- <file> for each file that was
        deleted. This allows us to delete a file, hit an interact link, then get a
        clean version of the file again.
        """

        status = subprocess.check_output(['git', 'status'], cwd=self.repo_dir)
        deleted_files = self.DELETED_FILE_REGEX.findall(status.decode('utf-8'))

        for filename in deleted_files:
            yield from execute_cmd(['git', 'checkout', '--', filename], cwd=self.repo_dir)
            logging.info('Resetted {}'.format(filename))

    def _make_commit(self):
        """
        Commit local changes
        """

        yield from execute_cmd(['git', 'checkout', self.branch_name], cwd=self.repo_dir)
        yield from execute_cmd(['git', 'add', '-A'], cwd=self.repo_dir)
        yield from execute_cmd(['git', 'config', 'user.email', '"gitautopull@email.com"'], cwd=self.repo_dir)
        yield from execute_cmd(['git', 'config', 'user.name', '"GitAutoPull"'], cwd=self.repo_dir)
        yield from execute_cmd(['git', 'commit', '-m', 'WIP'], cwd=self.repo_dir)
        logging.info('Made WIP commit')

    def _pull_and_resolve_conflicts(self):
        """
        Git pulls, resolving conflicts with -Xours
        """

        logging.info('Starting pull from {}'.format(self.git_url))

        yield from execute_cmd(['git', 'checkout', self.branch_name], cwd=self.repo_dir)
        yield from execute_cmd(['git', 'fetch'], cwd=self.repo_dir)
        yield from execute_cmd(['git', 'merge', '-Xours', 'origin/{}'.format(self.branch_name)], cwd=self.repo_dir)

        logging.info('Pulled from {}'.format(self.git_url))

    def repo_is_dirty(self):
        """
        Return true if repo is dirty
        """
        output = subprocess.check_output(['git', 'status', '--porcelain'], cwd=self.repo_dir)

        return self.MODIFIED_FILE_REGEX.search(output.decode('utf-8')) is not None


def main():
    """
    Synchronizes a github repository with a local repository.
    """
    logging.basicConfig(
        format='[%(asctime)s] %(levelname)s -- %(message)s',
        level=logging.DEBUG)

    parser = argparse.ArgumentParser(description='Synchronizes a github repository with a local repository.')
    parser.add_argument('--git-url', help='Url of the repo to sync', required=True)
    parser.add_argument('--branch-name', default='master', help='Branch of repo to sync')
    parser.add_argument('--repo-dir', default='./', help='Path to sync to')
    args = parser.parse_args()

    for line in GitPuller(
        args.git_url,
        args.branch_name,
        args.repo_dir
    ).pull_from_remote():
        print(line)
