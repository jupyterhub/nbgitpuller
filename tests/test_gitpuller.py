import os
import subprocess as sp
import glob
import time
from uuid import uuid4
import pytest
import tempfile

from traitlets.config.configurable import Configurable

from repohelpers import Remote, Pusher, Puller


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

        cloned_path = os.path.join(tempfile.gettempdir(), str(uuid4()))
        assert not os.path.exists(cloned_path)
        with Puller(remote, cloned_path) as puller:
            assert os.path.exists(os.path.join(puller.path, 'README.md'))
            assert puller.git('name-rev', '--name-only', 'HEAD') == 'master'
            assert puller.git('rev-parse', 'HEAD') == pusher.git('rev-parse', 'HEAD')


def command_line_test_helper(remote_path, branch, pusher_path):
    work_dir = "/".join(os.path.dirname(os.path.abspath(__file__)).split("/")[:-1]) + "/nbgitpuller"
    try:
        cmd = ['python3', 'pull.py', remote_path]
        if branch is not None:
            cmd += [branch]
        if pusher_path is not None:
            cmd += ['--target-dir', pusher_path]
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


def test_command_line_no_branch_passed():
    # so it should use the default branch
    branch = None
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
        with Puller(remote) as puller:
            puller.pull_all()
            assert not puller.gp.branch_exists("wrong")
            assert puller.gp.branch_exists("master")


def test_exception_branch_exists():
    with Remote() as remote, Pusher(remote) as pusher:
        pusher.push_file('README.md', '1')
        with Puller(remote) as puller:
            with pytest.raises(sp.CalledProcessError):
                orig_url = puller.gp.git_url
                puller.gp.git_url = ""
                puller.gp.branch_exists("wrong")
                puller.gp.git_url = orig_url

def test_resolve_default_branch():
    with Remote() as remote, Pusher(remote) as pusher:
        pusher.push_file('README.md', '1')
        with Puller(remote) as puller:
            assert puller.gp.resolve_default_branch() == "master"


def test_exception_resolve_default_branch():
    with Remote() as remote, Pusher(remote) as pusher:
        pusher.push_file('README.md', '1')
        with Puller(remote) as puller:
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


def test_reset_file_after_changes():
    """
    Test that we get the latest version of a file if we:
    - change the file locally
    - sync, so the change is preserved
    - delete the file, in order to reset it
    - sync again
    """
    with Remote() as remote, Pusher(remote) as pusher:
        pusher.push_file('README.md', 'original')

        with Puller(remote) as puller:
            puller.write_file('README.md', 'local change')
            pusher.push_file('README.md', 'remote change')
            puller.pull_all()

            # It should keep the local change
            assert puller.read_file('README.md') == 'local change'

            # Delete the local file manually and pull
            os.remove(os.path.join(puller.path, 'README.md'))
            puller.pull_all()

            # It should restore the remote change
            assert puller.read_file('README.md') == 'remote change'


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


def test_delete_remotely_modify_locally():
    """
    Test that we can delete a file upstream, and edit it at the same time locally
    """
    with Remote() as remote, Pusher(remote) as pusher:
        pusher.push_file('README.md', 'new')

        with Puller(remote) as puller:
            # Delete the file remotely
            pusher.git('rm', 'README.md')
            pusher.git('commit', '-m', 'Deleted file')

            # Edit locally
            pusher.push_file('README.md', 'HELLO')
            puller.pull_all()

            assert puller.read_file('README.md') == 'HELLO'


def test_diverged():
    """
    Test deleting a file upstream, and editing it locally.  This time we
    commit to create diverged brances.
    """
    with Remote() as remote, Pusher(remote) as pusher:
        pusher.push_file('README.md', 'new')

        with Puller(remote) as puller:
            # Delete the file remotely
            pusher.git('rm', 'README.md')
            pusher.git('commit', '-m', 'Deleted file')
            pusher.git('push', '-u', 'origin', 'master')

            # Edit locally
            puller.write_file('README.md', 'conflict')
            puller.git('add', 'README.md')
            puller.git('commit', '-m', 'Make conflicting change')

            # The local change should be kept
            puller.pull_all()
            assert puller.read_file('README.md') == 'conflict'


def test_diverged_reverse():
    """
    Test deleting a file locally, and editing it upstream.  We commit the changes
    to create diverged branches.  Like `test_diverged`, but flipped. 
    """
    with Remote() as remote, Pusher(remote) as pusher:
        pusher.push_file('README.md', 'new')

        with Puller(remote) as puller:
            # Delete the file locally
            puller.git('rm', 'README.md')
            puller.git('commit', '-m', 'Deleted file')

            # Edit the file remotely
            pusher.push_file('README.md', 'conflicting change')

            # Pulling should get the latest version of the file
            puller.pull_all()
            assert(puller.read_file('README.md') == 'conflicting change')


def test_diverged_multiple():
    """
    Test deleting a file upstream, and editing it locally.  We commit the changes
    to create diverged branches.

    Use two files, so git merge doesn't mention the conflict in the first line.

        puller: Auto-merging AFILE.txt
        puller: CONFLICT (modify/delete): BFILE.txt deleted in origin/master and modified in HEAD.  Version HEAD of BFILE.txt left in tree.
        puller: Automatic merge failed; fix conflicts and then commit the result.

    """
    with Remote() as remote, Pusher(remote) as pusher:
        pusher.push_file('AFILE.txt', 'new')
        pusher.push_file('BFILE.txt', 'new')

        with Puller(remote) as puller:
            # Remote changes - BFILE.txt deleted    
            pusher.write_file('AFILE.txt', 'changed remotely')
            pusher.git('add', 'AFILE.txt')
            pusher.git('rm', 'BFILE.txt')
            pusher.git('commit', '-m', 'Remote changes')
            pusher.git('push', '-u', 'origin', 'master')
  
            # Local changes - BFILE.txt edited
            puller.write_file('AFILE.txt', 'edited')
            puller.write_file('BFILE.txt', 'edited')
            puller.git('commit', '-am', 'Make conflicting change')

            puller.pull_all()
            assert puller.read_file('AFILE.txt') == 'edited'
            assert puller.read_file('BFILE.txt') == 'edited'


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
    with Remote() as remote, Pusher(remote) as pusher:
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
    with Puller(long_remote) as puller:
        assert count_loglines(puller) == 10


def test_shallow_clone(long_remote, clean_environment):
    """
    Test that shallow clones only have a portion of the git history
    """
    with Puller(long_remote, depth=4) as puller:
        assert count_loglines(puller) == 4


def test_shallow_clone_config(long_remote, clean_environment):
    """
    Test that shallow clones can be configured via parent Configurables
    """
    class TempConfig(Configurable):
        def __init__(self):
            super(TempConfig)
            self.config['GitPuller']['depth'] = 5

    with Puller(long_remote, parent=TempConfig()) as puller:
        assert count_loglines(puller) == 5


def test_environment_shallow_clone(long_remote, clean_environment):
    """
    Test that shallow clones respect the NBGITPULLER_DEPTH environment variable
    by default
    """
    os.environ['NBGITPULLER_DEPTH'] = "2"
    with Puller(long_remote) as puller:
        assert count_loglines(puller) == 2


def test_explicit_unshallow(long_remote, clean_environment):
    """
    Test that we can disable environment-specified shallow clones
    """
    os.environ['NBGITPULLER_DEPTH'] = "2"
    with Puller(long_remote, depth=0) as puller:
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
