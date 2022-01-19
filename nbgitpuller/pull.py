import os
import subprocess
import logging
import time
import argparse
import datetime
import pluggy
from traitlets import Integer, default
from traitlets.config import Configurable
from functools import partial
from . import plugin_hook_specs


class ContentProviderException(Exception):
    """
    Custom Exception thrown when the content_provider key specifying
    the downloader plugin is not installed or can not be found by the
    name given
    """
    def __init__(self, response=None):
        self.response = response

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


def setup_plugins(content_provider):
    """
    This automatically searches for and loads packages whose entrypoint is nbgitpuller. If found,
    the plugin manager object is returned and used to execute the hook implemented by
    the plugin.
    :param content_provider: this is the name of the content_provider; each plugin is named to identify the
    content_provider of the archive to be loaded(e.g. googledrive, dropbox, etc)
    :return: returns the PluginManager object used to call the implemented hooks of the plugin
    :raises: ContentProviderException -- this occurs when the content_provider parameter is not found
    """
    plugin_manager = pluggy.PluginManager("nbgitpuller")
    plugin_manager.add_hookspecs(plugin_hook_specs)
    num_loaded = plugin_manager.load_setuptools_entrypoints("nbgitpuller", name=content_provider)
    if num_loaded == 0:
        raise ContentProviderException(f"The content_provider key you supplied in the URL could not be found: {content_provider}")
    return plugin_manager


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
        self.content_provider = kwargs.pop("content_provider")
        self.repo_parent_dir = kwargs.pop("repo_parent_dir")
        self.other_kw_args = kwargs.pop("other_kw_args")
        self.repo_dir = repo_dir
        newargs = {k: v for k, v in kwargs.items() if v is not None}
        super(GitPuller, self).__init__(**newargs)

    def branch_exists(self, branch):
        """
        This checks to make sure the branch we are told to access
        exists in the repo
        """
        try:
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
        except subprocess.CalledProcessError:
            m = f"Problem accessing list of branches and/or tags: {self.git_url}"
            logging.exception(m)
            raise ValueError(m)

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

    def handle_archive_download(self):
        try:
            plugin_manager = setup_plugins(self.content_provider)
            other_kw_args = {k: v[0].decode() for k, v in self.other_kw_args}
            yield from plugin_manager.hook.handle_files(repo_parent_dir=self.repo_parent_dir,other_kw_args=other_kw_args)
            results = other_kw_args["handle_files_output"]
            self.repo_dir = self.repo_parent_dir + results["output_dir"]
            self.git_url = "file://" + results["origin_repo_path"]
        except ContentProviderException as c:
            raise c

    def handle_branch_name(self):
        if self.branch_name is None:
            self.branch_name = self.resolve_default_branch()
        elif not self.branch_exists(self.branch_name):
            raise ValueError(f"Branch: {self.branch_name} -- not found in repo: {self.git_url}")

    def pull(self):
        """
        if compressed archive download first.
        Execute pull of repo from a git repository(remote or temporary local created for compressed archives),
        while preserving user changes
        """
        # if content_provider is specified then we are dealing with compressed archive and not a git repo
        if self.content_provider is not None:
            yield from self.handle_archive_download()

        self.handle_branch_name()

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

        for filename in deleted_files:
            if filename:  # Filter out empty lines
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
            'git', 'log', '..origin/{}'.format(self.branch_name),
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
        # We explicitly set user info of the commits we are making, to keep that separate from
        # whatever author info is set in system / repo config by the user. We pass '-c' to git
        # itself (rather than to 'git commit') to temporarily set config variables. This is
        # better than passing --author, since git treats author separately from committer.
        if self.repo_is_dirty():
            yield from self.ensure_lock()
            yield from execute_cmd([
                'git',
                '-c', 'user.email=nbgitpuller@nbgitpuller.link',
                '-c', 'user.name=nbgitpuller',
                'commit',
                '-am', 'Automatic commit by nbgitpuller',
                '--allow-empty'
            ], cwd=self.repo_dir)

        # Merge master into local!
        yield from self.ensure_lock()
        yield from execute_cmd([
            'git',
            '-c', 'user.email=nbgitpuller@nbgitpuller.link',
            '-c', 'user.name=nbgitpuller',
            'merge',
            '-Xours', 'origin/{}'.format(self.branch_name)
        ], cwd=self.repo_dir)


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
    parser.add_argument('content_provider', default=None, help='If downloading compressed archive instead of using git repo set this(e.g. dropbox, googledrive, generic_web)', nargs='?')
    parser.add_argument('repo_parent_dir', default='.', help='Only used if downloading compressed archive, location of download', nargs='?')
    parser.add_argument('other_kw_args', default=None, help='you can pass any keyword args you want as a dict{"arg1":"value1","arg2":"value2"} -- could be used in downloader plugins', nargs='?')
    args = parser.parse_args()

    for line in GitPuller(
        args.git_url,
        args.repo_dir,
        branch=args.branch_name if args.branch_name else None,
        content_provider=args.content_provider if args.content_provider else None,
        repo_parent_dir=args.repo_parent_dir if args.repo_parent_dir else None,
        other_kw_args=args.other_kw_args if args.other_kw_args else None
    ).pull():
        print(line)


if __name__ == '__main__':
    main()
