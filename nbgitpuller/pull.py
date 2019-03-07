import os
import subprocess
import logging
import time
import argparse
import datetime
from traitlets import Integer, default
from traitlets.config import Configurable
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

class GitPuller(Configurable):
    depth = Integer(None, allow_none=True, config=True,
                    help="""
                    Depth (ie, commit count) to which to perform a
                    shallow git clone.

                    If not set, disables shallow clones.

                    Defaults to reading from the NBGITPULLER_DEPTH
                    environment variable.
                    """)

    @default('depth')
    def _depth_default(self):
        depth = os.environ.get('NBGITPULLER_DEPTH')
        if depth:
            return int(depth)
        return None

    def __init__(self, git_url, branch_name, repo_dir, **kwargs):
        assert git_url and branch_name

        self.git_url = git_url
        self.branch_name = branch_name
        self.repo_dir = repo_dir
        newargs = {k: v for k, v in kwargs.items() if v is not None}
        super(GitPuller, self).__init__(**newargs)

    def pull(self):
        """
        Pull selected repo from a remote git repository,
        while preserving user changes
        """
        if not os.path.exists(self.repo_dir):
            yield from self.initialize_repo()
        else:
            yield from self.update()

    def initialize_repo(self):
        """
        Clones repository & sets up usernames.
        """

        logging.info('Repo {} doesn\'t exist. Cloning...'.format(self.repo_dir))
        clone_args = ['git', 'clone']
        if self.depth and self.depth > 0:
            clone_args.extend(['--depth', str(self.depth)])
        clone_args.extend(['--branch', self.branch_name])
        clone_args.extend([self.git_url, self.repo_dir])
        yield from execute_cmd(clone_args)
        yield from execute_cmd(['git', 'config', 'user.email', 'nbgitpuller@example.com'], cwd=self.repo_dir)
        yield from execute_cmd(['git', 'config', 'user.name', 'nbgitpuller'], cwd=self.repo_dir)
        logging.info('Repo {} initialized'.format(self.repo_dir))


    def reset_deleted_files(self):
        """
        Runs the equivalent of git checkout -- <file> for each file that was
        deleted. This allows us to delete a file, hit an interact link, then get a
        clean version of the file again.
        """

        yield from self.ensure_lock()
        deleted_files = subprocess.check_output([
            'git', 'ls-files', '--deleted'
        ], cwd=self.repo_dir).decode().strip().split('\n')

        for filename in deleted_files:
            if filename:  # Filter out empty lines
                yield from execute_cmd(['git', 'checkout', '--', filename], cwd=self.repo_dir)

    def repo_is_dirty(self):
        """
        Return true if repo is dirty
        """
        try:
            subprocess.check_call(['git', 'diff-files', '--quiet'], cwd=self.repo_dir)
            # Return code is 0
            return False
        except subprocess.CalledProcessError:
            return True

    def update_remotes(self):
        """
        Do a git fetch so our remotes are up to date
        """
        yield from execute_cmd(['git', 'fetch'], cwd=self.repo_dir)

    def find_upstream_changed(self, kind):
        """
        Return list of files that have been changed upstream belonging to a particular kind of change
        """
        output = subprocess.check_output([
            'git', 'log', '{}..origin/{}'.format(self.branch_name, self.branch_name),
            '--oneline', '--name-status'
        ], cwd=self.repo_dir).decode()
        files = []
        for line in output.split('\n'):
            if line.startswith(kind):
                files.append(os.path.join(self.repo_dir, line.split('\t', 1)[1]))

        return files

    def ensure_lock(self):
        """
        Make sure we have the .git/lock required to do modifications on the repo

        This must be called before any git commands that modify state. This isn't guaranteed
        to be atomic, due to the nature of using files for locking. But it's the best we
        can do right now.
        """
        try:
            lockpath = os.path.join(self.repo_dir, '.git', 'index.lock')
            mtime = os.path.getmtime(lockpath)
            # A lock file does exist
            # If it's older than 10 minutes, we just assume it is stale and take over
            # If not, we fail with an explicit error.
            if time.time() - mtime > 600:
                yield "Stale .git/index.lock found, attempting to remove"
                os.remove(lockpath)
                yield "Stale .git/index.lock removed"
            else:
                raise Exception('Recent .git/index.lock found, operation can not proceed. Try again in a few minutes.')
        except FileNotFoundError:
            # No lock is held by other processes, we are free to go
            return

    def rename_local_untracked(self):
        """
        Rename local untracked files that would require pulls
        """
        # Find what files have been added!
        new_upstream_files = self.find_upstream_changed('A')
        for f in new_upstream_files:
            if os.path.exists(f):
                # If there's a file extension, put the timestamp before that
                ts = datetime.datetime.now().strftime('__%Y%m%d%H%M%S')
                path_head, path_tail = os.path.split(f)
                path_tail = ts.join(os.path.splitext(path_tail))
                new_file_name = os.path.join(path_head, path_tail)
                os.rename(f, new_file_name)
                yield 'Renamed {} to {} to avoid conflict with upstream'.format(f, new_file_name)


    def update(self):
        """
        Do the pulling if necessary
        """
        # Fetch remotes, so we know we're dealing with latest remote
        yield from self.update_remotes()

        # Rename local untracked files that might be overwritten by pull
        yield from self.rename_local_untracked()

        # Reset local files that have been deleted. We don't actually expect users to
        # delete something that's present upstream and expect to keep it. This prevents
        # unnecessary conflicts, and also allows users to click the link again to get
        # a fresh copy of a file they might have screwed up.
        yield from self.reset_deleted_files()

        # If there are local changes, make a commit so we can do merges when pulling
        # We also allow empty commits. On NFS (at least), sometimes repo_is_dirty returns a false
        # positive, returning True even when there are no local changes (git diff-files seems to return
        # bogus output?). While ideally that would not happen, allowing empty commits keeps us
        # resilient to that issue.
        if self.repo_is_dirty():
            yield from self.ensure_lock()
            yield from execute_cmd(['git', 'commit', '-am', 'WIP', '--allow-empty'], cwd=self.repo_dir)

        # Merge master into local!
        yield from self.ensure_lock()
        yield from execute_cmd(['git', 'merge', '-Xours', 'origin/{}'.format(self.branch_name)], cwd=self.repo_dir)



def main():
    """
    Synchronizes a github repository with a local repository.
    """
    logging.basicConfig(
        format='[%(asctime)s] %(levelname)s -- %(message)s',
        level=logging.DEBUG)

    parser = argparse.ArgumentParser(description='Synchronizes a github repository with a local repository.')
    parser.add_argument('git_url', help='Url of the repo to sync')
    parser.add_argument('branch_name', default='master', help='Branch of repo to sync', nargs='?')
    parser.add_argument('repo_dir', default='.', help='Path to clone repo under', nargs='?')
    args = parser.parse_args()

    for line in GitPuller(
        args.git_url,
        args.branch_name,
        args.repo_dir
    ).pull():
        print(line)
