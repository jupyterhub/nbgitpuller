import os
import shutil
import subprocess as sp
import glob
import time
import pytest

from traitlets.config.configurable import Configurable

from nbgitpuller import GitPuller


class Repository:
    def __init__(self, path='remote'):
        self.path = path

    def __enter__(self):
        os.mkdir(self.path)
        self.git('init', '--bare')
        return self

    def __exit__(self, *args):
        shutil.rmtree(self.path)

    def write_file(self, path, content):
        with open(os.path.join(self.path, path), 'w') as f:
            f.write(content)

    def read_file(self, path):
        with open(os.path.join(self.path, path)) as f:
            return f.read()

    def git(self, *args):
        return sp.check_output(
            ['git'] + list(args),
            cwd=self.path,
            stderr=sp.STDOUT
        ).decode().strip()


class Remote(Repository):
    pass


class Pusher(Repository):
    def __init__(self, remote, path='pusher'):
        self.remote = remote
        super().__init__(path=path)

    def __enter__(self):
        sp.check_output(['git', 'clone', self.remote.path, self.path])
        self.git('config', '--local', 'user.email', 'pusher@example.com')
        self.git('config', '--local', 'user.name', 'pusher')
        return self

    def push_file(self, path, content):
        self.write_file(path, content)
        self.git('add', path)
        self.git('commit', '-am', 'Ignore the message')
        self.git('push', 'origin', 'master')


class Puller(Repository):
    def __init__(self, remote, path='puller', branch="master", *args, **kwargs):
        super().__init__(path)
        remotepath = "file://%s" % os.path.abspath(remote.path)
        self.gp = GitPuller(remotepath, path, branch=branch, *args, **kwargs)

    def pull_all(self):
        for line in self.gp.pull():
            print('{}: {}'.format(self.path, line.rstrip()))

    def __enter__(self):
        print()
        self.pull_all()
        self.git('config', '--local', 'user.email', 'puller@example.com')
        self.git('config', '--local', 'user.name', 'puller')
        return self


# Tests to write:
# 1. Initialize puller with gitpuller, test for user config & commit presence
# 2. Push commit with pusher, pull with puller, valiate that nothing has changeed
# 3. Delete file in puller, run puller, make sure file is back
# 4. Make change in puller to file, make change in pusher to different part of file, run puller
# 5. Make change in puller to file, make change in pusher to same part of file, run puller
# 6. Make untracked file in puller, add file with same name to pusher, run puller


def test_initialize():
    with Remote() as remote, Pusher(remote) as pusher:
        pusher.push_file('README.md', '1')

        assert not os.path.exists('puller')
        with Puller(remote, 'puller') as puller:
            assert os.path.exists(os.path.join(puller.path, 'README.md'))
            assert puller.git('name-rev', '--name-only', 'HEAD') == 'master'
            assert puller.git('rev-parse', 'HEAD') == pusher.git('rev-parse', 'HEAD')


def command_line_test_helper(remote_path, branch, pusher_path):
    work_dir = "/".join(os.path.dirname(os.path.abspath(__file__)).split("/")[:-1]) + "/nbgitpuller"
    try:
        cmd = ['python3', 'pull.py', remote_path, branch, pusher_path]
        sp.check_output(
            cmd,
            cwd=work_dir
        ).decode()
        return True
    except Exception:
        return False


def test_command_line_existing_branch():
    branch = "master"
    with Remote() as remote, Pusher(remote) as pusher:
        pusher.push_file('README.md', '1')
        remotepath = "file://%s" % os.path.abspath(remote.path)
        pusherpath = os.path.abspath(pusher.path)
        subprocess_result = command_line_test_helper(remotepath, branch, pusherpath)
    assert subprocess_result


def test_command_line_default_branch():
    branch = ""
    with Remote() as remote, Pusher(remote) as pusher:
        pusher.push_file('README.md', '1')
        remotepath = "file://%s" % os.path.abspath(remote.path)
        pusherpath = os.path.abspath(pusher.path)
        subprocess_result = command_line_test_helper(remotepath, branch, pusherpath)
    assert subprocess_result


def test_command_line_non_existing_branch():
    branch = "wrong"
    with Remote() as remote, Pusher(remote) as pusher:
        pusher.push_file('README.md', '1')
        remotepath = "file://%s" % os.path.abspath(remote.path)
        pusherpath = os.path.abspath(pusher.path)
        subprocess_result = command_line_test_helper(remotepath, branch, pusherpath)
    assert not subprocess_result


def test_branch_exists():
    with Remote() as remote, Pusher(remote) as pusher:
        pusher.push_file('README.md', '1')
        with Puller(remote, 'puller') as puller:
            assert not puller.gp.branch_exists("wrong")
            assert puller.gp.branch_exists("master")


def test_exception_branch_exists():
    with Remote() as remote, Pusher(remote) as pusher:
        pusher.push_file('README.md', '1')
        with Puller(remote, 'puller') as puller:
            orig_url = puller.gp.git_url
            puller.gp.git_url = ""
            try:
                puller.gp.branch_exists("wrong")
            except Exception as e:
                assert type(e) == ValueError
            puller.gp.git_url = orig_url


def test_resolve_default_branch():
    with Remote() as remote, Pusher(remote) as pusher:
        pusher.push_file('README.md', '1')
        with Puller(remote, 'puller') as puller:
            assert puller.gp.resolve_default_branch() == "master"


def test_exception_resolve_default_branch():
    with Remote() as remote, Pusher(remote) as pusher:
        pusher.push_file('README.md', '1')
        with Puller(remote, 'puller') as puller:
            orig_url = puller.gp.git_url
            puller.gp.git_url = ""
            try:
                puller.gp.resolve_default_branch()
            except Exception as e:
                assert type(e) == ValueError
            puller.gp.git_url = orig_url


def test_simple_push_pull():
    """
    Test the 'happy path' push/pull interaction

    1. Push a file to remote, pull (initially) to make sure we get it
    2. Modify file & push to remote, pull to make sure we get update
    3. Add new file to remote, pull to make sure we get it
    4. Delete new file to remote, pull to make sure it is gone

    No modifications are done in the puller repo here, so we do not
    exercise any merging behavior.
    """
    with Remote() as remote, Pusher(remote) as pusher:
        pusher.push_file('README.md', '1')

        with Puller(remote) as puller:
            assert puller.git('rev-parse', 'HEAD') == pusher.git('rev-parse', 'HEAD')
            assert puller.read_file('README.md') == pusher.read_file('README.md') == '1'

            pusher.push_file('README.md', '2')
            puller.pull_all()

            assert puller.git('rev-parse', 'HEAD') == pusher.git('rev-parse', 'HEAD')
            assert puller.read_file('README.md') == pusher.read_file('README.md') == '2'

            pusher.push_file('another-file', '3')

            puller.pull_all()

            assert puller.git('rev-parse', 'HEAD') == pusher.git('rev-parse', 'HEAD')
            assert puller.read_file('another-file') == pusher.read_file('another-file') == '3'

            pusher.git('rm', 'another-file')
            pusher.git('commit', '-m', 'Removing File')
            pusher.git('push', 'origin', 'master')

            puller.pull_all()

            assert puller.git('rev-parse', 'HEAD') == pusher.git('rev-parse', 'HEAD')
            assert not os.path.exists(os.path.join(puller.path, 'another-file'))


def test_git_lock():
    """
    Test the 'happy path', but with stale/unstale git locks
    """
    with Remote() as remote, Pusher(remote) as pusher:
        pusher.push_file('README.md', '1')

        with Puller(remote) as puller:
            pusher.push_file('README.md', '2')

            puller.write_file('.git/index.lock', '')

            exception_raised = False
            try:
                puller.pull_all()
            except Exception:
                exception_raised = True
            assert exception_raised

            new_time = time.time() - 700
            os.utime(os.path.join(puller.path, '.git', 'index.lock'), (new_time, new_time))

            puller.pull_all()
            assert puller.git('rev-parse', 'HEAD') == pusher.git('rev-parse', 'HEAD')


def test_merging_simple():
    """
    Test that when we change local & remote, local changes are preferred
    """
    with Remote() as remote, Pusher(remote) as pusher:
        pusher.push_file('README.md', '1')

        with Puller(remote) as puller:
            assert puller.read_file('README.md') == pusher.read_file('README.md') == '1'

            puller.write_file('README.md', '2')

            pusher.push_file('README.md', '3')

            puller.pull_all()

            # There should be a commit made *before* the pull that has our explicit
            # authorship, to record that it was made by nbgitpuller
            assert puller.git('show', '-s', '--format="%an <%ae>"', 'HEAD^1') == '"nbgitpuller <nbgitpuller@nbgitpuller.link>"'

            assert puller.read_file('README.md') == '2'
            assert pusher.read_file('README.md') == '3'

            # Make sure that further pushes to other files are reflected
            pusher.push_file('another-file', '4')

            puller.pull_all()

            assert puller.read_file('another-file') == pusher.read_file('another-file') == '4'

            # Make sure our merging works across commits

            pusher.push_file('README.md', '5')
            puller.pull_all()

            assert puller.read_file('README.md') == '2'


def test_merging_after_commit():
    """
    Test that merging works even after we make a commit locally
    """
    with Remote() as remote, Pusher(remote) as pusher:
        pusher.push_file('README.md', '1')

        with Puller(remote) as puller:
            assert puller.read_file('README.md') == pusher.read_file('README.md') == '1'

            puller.write_file('README.md', '2')
            puller.git('commit', '-am', 'Local change')

            puller.pull_all()

            assert puller.read_file('README.md') == '2'
            assert pusher.read_file('README.md') == '1'

            pusher.push_file('README.md', '3')
            puller.pull_all()

            # Check if there is a merge commit
            parent_commits = puller.git('show', '-s', '--format="%P"', 'HEAD').strip().split(' ')
            assert(len(parent_commits) == 2)


def test_untracked_puller():
    """
    Test that untracked files in puller are preserved when pulling
    """
    with Remote() as remote, Pusher(remote) as pusher:
        pusher.push_file('README.md', '1')

        with Puller(remote) as puller:
            pusher.push_file('another-file', '2')

            puller.write_file('another-file', '3')

            puller.pull_all()
            assert puller.read_file('another-file') == '2'
            # Find file that was created!
            renamed_file = glob.glob(os.path.join(puller.path, 'another-file_*'))[0]
            assert puller.read_file(os.path.basename(renamed_file)) == '3'


def test_reset_file():
    """
    Test that deleting files locally & pulling restores pristine copy
    """
    with Remote() as remote, Pusher(remote) as pusher:
        pusher.push_file('README.md', '1')
        pusher.push_file('unicode🙂.txt', '2')

        with Puller(remote) as puller:
            os.remove(os.path.join(puller.path, 'README.md'))
            os.remove(os.path.join(puller.path, 'unicode🙂.txt'))

            puller.pull_all()

            assert puller.git('rev-parse', 'HEAD') == pusher.git('rev-parse', 'HEAD')
            assert puller.read_file('README.md') == pusher.read_file('README.md') == '1'
            assert puller.read_file('unicode🙂.txt') == pusher.read_file('unicode🙂.txt') == '2'

def test_delete_conflicted_file():
    """
    Test that after deleting a file that had a conflict, we can still pull
    """
    with Remote() as remote, Pusher(remote) as pusher:
        pusher.push_file('README.md', 'hello')

        with Puller(remote) as puller:
            # Change a file locally
            puller.write_file('README.md', 'student changed')

            # Sync will keep the local change
            puller.pull_all()            
            assert puller.read_file('README.md') == 'student changed'

            # Delete previously changed file
            os.remove(os.path.join(puller.path, 'README.md'))

            # Make a change remotely.  We should be able to pull it
            pusher.push_file('new_file.txt', 'hello world')
            puller.pull_all()


def test_delete_locally_and_remotely():
    """
    Test that sync works after deleting a file locally and remotely
    """
    with Remote() as remote, Pusher(remote) as pusher:
        pusher.push_file('README.md', '1')

        with Puller(remote) as puller:
            assert puller.read_file('README.md') == pusher.read_file('README.md') == '1'

            # Delete locally (without git rm)
            os.remove(os.path.join(puller.path, 'README.md'))

            # Delete remotely
            pusher.git('rm', 'README.md')
            
            # Create another change to pull
            pusher.push_file('another_file.txt', '2')
            puller.pull_all()

            assert not os.path.exists(os.path.join(puller.path, 'README.md'))
            assert puller.read_file('another_file.txt') == '2'


def test_sync_with_staged_changes():
    """
    Test that we can sync even if there are staged changess
    """

    with Remote() as remote, Pusher(remote) as pusher:
        pusher.push_file('README.md', '1')

        with Puller(remote) as puller:
            assert puller.read_file('README.md') == pusher.read_file('README.md') == '1'

            # Change a file locally and remotely
            puller.write_file('README.md', 'student changed')
            pusher.push_file('README.md', 'teacher changed')
            
            # Stage the local change, but do not commit
            puller.git('add', 'README.md')

            # Try to sync
            puller.pull_all()


@pytest.fixture(scope='module')
def long_remote():
    with Remote("long_remote") as remote, Pusher(remote, "lr_pusher") as pusher:
        for i in range(0, 10):
            pusher.git('commit', '--allow-empty', '-m', "Empty message %d" % i)
            pusher.git('push', 'origin', 'master')

        yield remote


@pytest.fixture(scope="function")
def clean_environment():
    """
    Save and restore the state of named VARIABLES before, during, and
    after tests.
    """

    VARIABLES = ['NBGITPULLER_DEPTH']
    backups = {}
    for var in VARIABLES:
        backups[var] = os.environ.get(var)
        if backups[var]:
            del os.environ[var]

    yield

    for var in backups:
        if backups[var]:
            os.environ[var] = backups[var]
        elif os.environ.get(var):
            del os.environ[var]


def count_loglines(repository):
    return len(repository.git('log', '--oneline').split("\n"))


def test_unshallow_clone(long_remote, clean_environment):
    """
    Sanity-test that clones with 10 commits have 10 log entries
    """
    os.environ['NBGITPULLER_DEPTH'] = "0"
    with Puller(long_remote, 'normal') as puller:
        assert count_loglines(puller) == 10


def test_shallow_clone(long_remote, clean_environment):
    """
    Test that shallow clones only have a portion of the git history
    """
    with Puller(long_remote, 'shallow4', depth=4) as puller:
        assert count_loglines(puller) == 4


def test_shallow_clone_config(long_remote, clean_environment):
    """
    Test that shallow clones can be configured via parent Configurables
    """
    class TempConfig(Configurable):
        def __init__(self):
            super(TempConfig)
            self.config['GitPuller']['depth'] = 5

    with Puller(long_remote, 'shallow4', parent=TempConfig()) as puller:
        assert count_loglines(puller) == 5


def test_environment_shallow_clone(long_remote, clean_environment):
    """
    Test that shallow clones respect the NBGITPULLER_DEPTH environment variable
    by default
    """
    os.environ['NBGITPULLER_DEPTH'] = "2"
    with Puller(long_remote, 'shallow_env') as puller:
        assert count_loglines(puller) == 2


def test_explicit_unshallow(long_remote, clean_environment):
    """
    Test that we can disable environment-specified shallow clones
    """
    os.environ['NBGITPULLER_DEPTH'] = "2"
    with Puller(long_remote, 'explicitly_full', depth=0) as puller:
        assert count_loglines(puller) == 10


def test_pull_on_shallow_clone(long_remote, clean_environment):
    """
    Test that we can perform a pull on a shallow clone
    """
    with Puller(long_remote, depth=0) as shallow_puller:
        with Pusher(long_remote) as pusher:
            pusher.push_file('test_file', 'test')

            orig_head = shallow_puller.git('rev-parse', 'HEAD')
            shallow_puller.pull_all()
            new_head = shallow_puller.git('rev-parse', 'HEAD')
            upstream_head = long_remote.git('rev-parse', 'HEAD')

            assert orig_head != new_head
            assert new_head == upstream_head

            pusher.git('push', '--force', 'origin', '%s:master' % orig_head)
