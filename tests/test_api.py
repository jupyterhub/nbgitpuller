import os
from http.client import HTTPConnection
import subprocess
from time import sleep
from urllib.parse import quote
from uuid import uuid4
import pytest

PORT = os.getenv('TEST_PORT', 18888)


def request_api(params, host='localhost'):
    h = HTTPConnection(host, PORT, 10)
    query = '&'.join('{}={}'.format(k, quote(v)) for (k, v) in params.items())
    url = '/git-pull/api?token=secret&{}'.format(query)
    h.request('GET', url)
    return h.getresponse()


class TestNbGitPullerApi:

    def setup(self):
        self.jupyter_proc = None

    def teardown(self):
        if self.jupyter_proc:
            self.jupyter_proc.kill()

    def start_jupyter(self, jupyterdir, extraenv, backend_type):
        env = os.environ.copy()
        env.update(extraenv)
        if "server" in backend_type:
            command = [
                'jupyter-server',
                '--NotebookApp.token=secret',
                '--port={}'.format(PORT),
            ]
        else:
            command = [
                'jupyter-notebook',
                '--no-browser',
                '--NotebookApp.token=secret',
                '--port={}'.format(PORT),
            ]
        self.jupyter_proc = subprocess.Popen(command, cwd=jupyterdir, env=env)
        sleep(2)

    @pytest.mark.parametrize(
        "backend_type",
        [
            ("jupyter-server"),
            # ("jupyter-notebook"),
        ],
    )
    def test_clone_default(self, tmpdir, backend_type):
        """
        Tests use of 'repo' and 'branch' parameters.
        """
        jupyterdir = str(tmpdir)
        self.start_jupyter(jupyterdir, {}, backend_type)
        params = {
            'repo': 'https://github.com/binder-examples/jupyter-extension',
            'branch': 'master',
        }
        r = request_api(params)
        assert r.code == 200
        s = r.read().decode()
        print(s)
        assert '--branch master' in s
        assert "Cloning into '{}/{}'".format(jupyterdir, 'jupyter-extension') in s
        assert os.path.isdir(os.path.join(jupyterdir, 'jupyter-extension', '.git'))

    @pytest.mark.parametrize(
        "backend_type",
        [
            ("jupyter-server"),
            ("jupyter-notebook"),
        ],
    )
    def test_clone_targetpath(self, tmpdir, backend_type):
        """
        Tests use of 'targetpath' parameter.
        """
        jupyterdir = str(tmpdir)
        target = str(uuid4())
        self.start_jupyter(jupyterdir, {}, backend_type)
        params = {
            'repo': 'https://github.com/binder-examples/jupyter-extension',
            'branch': 'master',
            'targetpath': target,
        }
        r = request_api(params)
        assert r.code == 200
        s = r.read().decode()
        print(s)
        assert "Cloning into '{}/{}'".format(jupyterdir, target) in s
        assert os.path.isdir(os.path.join(jupyterdir, target, '.git'))

    @pytest.mark.parametrize(
        "backend_type",
        [
            ("jupyter-server"),
            ("jupyter-notebook"),
        ],
    )
    def test_clone_parenttargetpath(self, tmpdir, backend_type):
        """
        Tests use of the NBGITPULLER_PARENTPATH environment variable.
        """
        jupyterdir = str(tmpdir)
        parent = str(uuid4())
        target = str(uuid4())
        self.start_jupyter(jupyterdir, {'NBGITPULLER_PARENTPATH': parent}, backend_type)
        params = {
            'repo': 'https://github.com/binder-examples/jupyter-extension',
            'branch': 'master',
            'targetpath': target,
        }
        r = request_api(params)
        assert r.code == 200
        s = r.read().decode()
        print(s)
        assert "Cloning into '{}/{}/{}'".format(jupyterdir, parent, target) in s
        assert os.path.isdir(os.path.join(jupyterdir, parent, target, '.git'))
