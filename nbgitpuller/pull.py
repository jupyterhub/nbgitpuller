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
    # Explicitly set LANG=C, as `git` commandline output will be different if
    # the user environment has a different locale set!
    kwargs['env'] = dict(os.environ, LANG='C')

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
    depth = Integer(
        config=True,
        help="""
        Depth (ie, commit count) of clone operations. Set this to 0 to make a
        full depth clone.

        Defaults to the value of the environment variable NBGITPULLER_DEPTH, or
        1 if the the environment variable isn't set.
        """
    )

    @default('depth')
    def _depth_default(self):
        """This is a workaround for setting the same default directly in the
        definition of the traitlet above. Without it, the test fails because a
        change in the environment variable has no impact. I think this is a
        consequence of the tests not starting with a totally clean environment
        where the GitPuller class hadn't been loaded already."""
        return int(os.environ.get('NBGITPULLER_DEPTH', 1))

    def __init__(self, git_url, repo_dir, **kwargs):
        assert git_url

        self.git_url = git_url
        self.branch_name = kwargs.pop("branch")

        if self.branch_name is None:
            self.branch_name = self.resolve_default_branch()
        elif not self.branch_exists(self.branch_name):
            raise ValueError(f"Branch: {self.branch_name} -- not found in repo: {self.git_url}")

        self.repo_dir = repo_dir
        newargs = {k: v for k, v in kwargs.items() if v is not None}
        super(GitPuller, self).__init__(**newargs)

    def branch_exists(self, branch):
        """
        This checks to make sure the branch we are told to access
        exists in the repo
        """
        heads = subprocess.run(
            ["git", "ls-remote", "--heads", "--", self.git_url],
            capture_output=True,
            text=True,
            check=True
        )
        tags = subprocess.run(
            ["git", "ls-remote", "--tags", "--", self.git_url],
            capture_output=True,
            text=True,
            check=True
        )
        lines = heads.stdout.splitlines() + tags.stdout.splitlines()
        branches = []
        for line in lines:
            _, ref = line.split()
            refs, heads, branch_name = ref.split("/", 2)
            branches.append(branch_name)
        return branch in branches

    def resolve_default_branch(self):
        """
        This will resolve the default branch of the repo in
        the case where the branch given does not exist
        """
        try:
            head_branch = subprocess.run(
                ["git", "ls-remote", "--symref", "--", self.git_url, "HEAD"],
                capture_output=True,
                text=True,
                check=True
            )
            for line in head_branch.stdout.splitlines():
                if line.startswith("ref:"):
                    # line resembles --> ref: refs/heads/main HEAD
                    _, ref, head = line.split()
                    refs, heads, branch_name = ref.split("/", 2)
                    return branch_name
            raise ValueError(f"default branch not found in {self.git_url}")
        except subprocess.CalledProcessError:
            m = f"Problem accessing HEAD branch: {self.git_url}"
            logging.exception(m)
            raise ValueError(m)

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
        Clones repository
        """
        logging.info('Repo {} doesn\'t exist. Cloning...'.format(self.repo_dir))
        clone_args = ['git', 'clone']
        if self.depth and self.depth > 0:
            clone_args.extend(['--depth', str(self.depth)])
        clone_args.extend(['--branch', self.branch_name])
        clone_args.extend(["--", self.git_url, self.repo_dir])
        yield from execute_cmd(clone_args)
        logging.info('Repo {} initialized'.format(self.repo_dir))

    def reset_deleted_files(self):
        """
        Runs the equivalent of git checkout -- <file> for each file that was
        deleted. This allows us to delete a file, hit an interact link, then get a
        clean version of the file again.
        """

        yield from self.ensure_lock()
        deleted_files = subprocess.check_output([
            'git', 'ls-files', '--deleted', '-z'
        ], cwd=self.repo_dir).decode().strip().split('\0')

        upstream_deleted = self.find_upstream_changed('D')
        for filename in deleted_files:
            if not filename:
                # filter out empty lines
                continue

            if filename in upstream_deleted:
                # deleted in _both_, avoid conflict with git 2.40 by checking it out
                # even though it's just about to be deleted
                yield from execute_cmd(
                    ['git', 'checkout', 'HEAD', '--', filename], cwd=self.repo_dir
                )
            else:
                # not deleted in upstream, restore with checkout
                yield from execute_cmd(['git', 'checkout', 'origin/{}'.format(self.branch_name), '--', filename], cwd=self.repo_dir)

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
            'git', 'diff', '..origin/{}'.format(self.branch_name),
            '--name-status'
        ], cwd=self.repo_dir).decode()
        files = []
        for line in output.split('\n'):
            if line.startswith(kind):
                files.append(line.split('\t', 1)[1])

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
            f = os.path.join(self.repo_dir, f)
            if os.path.exists(f):
                # If there's a file extension, put the timestamp before that
                ts = datetime.datetime.now().strftime('__%Y%m%d%H%M%S')
                path_head, path_tail = os.path.split(f)
                path_tail = ts.join(os.path.splitext(path_tail))
                new_file_name = os.path.join(path_head, path_tail)
                os.rename(f, new_file_name)
                yield 'Renamed {} to {} to avoid conflict with upstream'.format(f, new_file_name)

    def merge(self):
        """
        Merges branch from origin into current branch, resolving conflicts when possible.

        Resolves conflicts in two ways:

        - Passes `-Xours` to git, setting merge-strategy to preserve changes made by the
          user whererver possible
        - Detect (modify/delete) conflicts, where the user has locally modified something
          that was deleted upstream. We just keep the local file.
        """
        modify_delete_conflict = False
        try:
            for line in execute_cmd([
                'git',
                '-c', 'user.email=nbgitpuller@nbgitpuller.link',
                '-c', 'user.name=nbgitpuller',
                'merge',
                '-Xours', 'origin/{}'.format(self.branch_name)
            ],
            cwd=self.repo_dir):
                yield line
                # Detect conflict caused by one branch
                if line.startswith("CONFLICT (modify/delete)"):
                    modify_delete_conflict = True
        except subprocess.CalledProcessError:
            if not modify_delete_conflict:
                raise

        if modify_delete_conflict:
            yield "Caught modify/delete conflict, trying to resolve"
            # If a file was deleted on one branch, and modified on another,
            # we just keep the modified file.  This is done by `git add`ing it.
            yield from self.commit_all()

    def commit_all(self):
        """
        Creates a new commit with all current changes
        """
        yield from execute_cmd([
            'git',
            # We explicitly set user info of the commits we are making, to keep that separate from
            # whatever author info is set in system / repo config by the user. We pass '-c' to git
            # itself (rather than to 'git commit') to temporarily set config variables. This is
            # better than passing --author, since git treats author separately from committer.
            '-c', 'user.email=nbgitpuller@nbgitpuller.link',
            '-c', 'user.name=nbgitpuller',
            'commit',
            '-am', 'Automatic commit by nbgitpuller',
            # We allow empty commits. On NFS (at least), sometimes repo_is_dirty returns a false
            # positive, returning True even when there are no local changes (git diff-files seems to return
            # bogus output?). While ideally that would not happen, allowing empty commits keeps us
            # resilient to that issue.
            '--allow-empty'
        ], cwd=self.repo_dir)

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

        # Unstage any changes, otherwise the merge might fail.
        # The following command resets the index, but keeps the working tree.  All changes
        # to files will be preserved, but they are no longer staged for commit.
        yield from execute_cmd(['git', 'reset', '--mixed'], cwd=self.repo_dir)

        # If there are local changes, make a commit so we can do merges when pulling
        if self.repo_is_dirty():
            yield from self.ensure_lock()
            yield from self.commit_all()

        # Merge master into local!
        yield from self.ensure_lock()
        yield from self.merge()


def main():
    """
    Synchronizes a github repository with a local repository.
    """
    logging.basicConfig(
        format='[%(asctime)s] %(levelname)s -- %(message)s',
        level=logging.DEBUG)

    parser = argparse.ArgumentParser(description='Synchronizes a github repository with a local repository.')
    parser.add_argument('git_url', help='Url of the repo to sync')
    parser.add_argument('branch_name', default=None, help='Branch of repo to sync', nargs='?')
    parser.add_argument('repo_dir', default='.', help='Path to clone repo under', nargs='?')
    args = parser.parse_args()

    for line in GitPuller(
        args.git_url,
        args.repo_dir,
        branch=args.branch_name if args.branch_name else None
    ).pull():
        print(line)


if __name__ == '__main__':
    main()
