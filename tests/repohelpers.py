"""
Helper classes for creating git repos
"""
import os
import tempfile
import shutil
import subprocess as sp
from uuid import uuid4

from nbgitpuller import GitPuller


class Repository:
    def __init__(self, path=None):
        if path is None:
            path = os.path.join(tempfile.gettempdir(), str(uuid4()))
        self.path = path

    def __enter__(self):
        os.makedirs(self.path, exist_ok=True)
        self.git('init', '--bare', '--initial-branch=master')
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
    def __init__(self, remote, path=None):
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
    def __init__(self, remote, path=None, branch="master", *args, **kwargs):
        super().__init__(path)
        remotepath = "file://%s" % os.path.abspath(remote.path)
        self.gp = GitPuller(remotepath, self.path, branch=branch, *args, **kwargs)

    def pull_all(self):
        for line in self.gp.pull():
            print('{}: {}'.format(self.path, line.rstrip()))

    def __enter__(self):
        print()
        self.pull_all()
        self.git('config', '--local', 'user.email', 'puller@example.com')
        self.git('config', '--local', 'user.name', 'puller')
        return self

