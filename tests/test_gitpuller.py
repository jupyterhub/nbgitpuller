import os
import shutil
import subprocess as sp
import glob
import time
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
    def __init__(self, remote, path='puller'):
        super().__init__(path)
        self.gp = GitPuller(remote.path, 'master', path)

    def __enter__(self):
        for line in self.gp.pull():
            print(line)
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
            for l in puller.gp.pull():
                print(puller.path + l)

            assert puller.git('rev-parse', 'HEAD') == pusher.git('rev-parse', 'HEAD')
            assert puller.read_file('README.md') == pusher.read_file('README.md') == '2'

            pusher.push_file('another-file', '3')

            for l in puller.gp.pull():
                print(l)

            assert puller.git('rev-parse', 'HEAD') == pusher.git('rev-parse', 'HEAD')
            assert puller.read_file('another-file') == pusher.read_file('another-file') == '3'

            pusher.git('rm', 'another-file')
            pusher.git('commit', '-m', 'Removing File')
            pusher.git('push', 'origin', 'master')

            for l in puller.gp.pull():
                print(l)

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
                for l in puller.gp.pull():
                    print(puller.path + l)
            except Exception:
                exception_raised = True
            assert exception_raised

            new_time = time.time() - 700
            os.utime(os.path.join(puller.path, '.git', 'index.lock'), (new_time, new_time))

            for l in puller.gp.pull():
                print(puller.path + l)
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

            for l in puller.gp.pull():
                print(l)

            assert puller.read_file('README.md') == '2'
            assert pusher.read_file('README.md') == '3'

            # Make sure that further pushes to other files are reflected
            pusher.push_file('another-file', '4')

            for l in puller.gp.pull():
                print(l)

            assert puller.read_file('another-file') == pusher.read_file('another-file') == '4'

            # Make sure our merging works across commits

            pusher.push_file('README.md', '5')
            for l in puller.gp.pull():
                print(l)

            assert puller.read_file('README.md') == '2'


def test_untracked_puller():
    """
    Test that untracked files in puller are preserved when pulling
    """
    with Remote() as remote, Pusher(remote) as pusher:
        pusher.push_file('README.md', '1')

        with Puller(remote) as puller:
            pusher.push_file('another-file', '2')

            puller.write_file('another-file', '3')

            for l in puller.gp.pull():
                print(l)
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

        with Puller(remote) as puller:
            os.remove(os.path.join(puller.path, 'README.md'))

            for l in puller.gp.pull():
                print(l)

            assert puller.git('rev-parse', 'HEAD') == pusher.git('rev-parse', 'HEAD')
            assert puller.read_file('README.md') == pusher.read_file('README.md') == '1'
