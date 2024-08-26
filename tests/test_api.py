import os
from http.client import HTTPConnection
import subprocess
import time
from urllib.parse import urlencode
from uuid import uuid4
import notebook
import pytest

from repohelpers import Pusher, Remote

PORT = os.getenv('TEST_PORT', 18888)


def request_api(params, host='localhost'):
    query_args = {"token": "secret"}
    query_args.update(params)
    query = urlencode(query_args)
    url = f'/git-pull/api?{query}'
    h = HTTPConnection(host, PORT, 10)
    h.request('GET', url)
    return h.getresponse()

def wait_for_server(host='localhost', port=PORT, timeout=10):
    """Wait for an HTTP server to be responsive"""
    t = 0.1
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            h = HTTPConnection(host, port, 10)
            h.request("GET", "/")
            r = h.getresponse()
        except Exception as e:
            print(f"Server not ready: {e}")
            time.sleep(t)
            t *= 2
            t = min(t, 1)
        else:
            # success
            return
    assert False, f"Server never showed up at http://{host}:{port}"


@pytest.fixture
def jupyterdir(tmpdir):
    path = tmpdir.join("jupyter")
    path.mkdir()
    return str(path)


@pytest.fixture(params=["jupyter-server", "jupyter-notebook"])
def jupyter_server(request, tmpdir, jupyterdir):
    # allow passing extra_env via @pytest.mark.jupyter_server(extra_env={"key": "value"})
    if "jupyter_server" in request.keywords:
        extra_env = request.keywords["jupyter_server"].kwargs.get("extra_env")
    else:
        extra_env = None

    backend_type = request.param

    env = os.environ.copy()
    # avoid interacting with user configuration, state
    env["JUPYTER_CONFIG_DIR"] = str(tmpdir / "dotjupyter")
    env["JUPYTER_RUNTIME_DIR"] = str(tmpdir / "runjupyter")

    if extra_env:
        env.update(extra_env)

    extension_command = ["jupyter", "server", "extension"]
    if backend_type == "jupyter-server":
        command = [
            'jupyter-server',
            '--ServerApp.token=secret',
            '--port={}'.format(PORT),
        ]
    elif backend_type == "jupyter-notebook":
        command = [
            'jupyter-notebook',
            '--no-browser',
            '--NotebookApp.token=secret',
            '--port={}'.format(PORT),
        ]
        # notebook <7 require "jupyter serverextension" instead of "jupyter
        # server extension"
        if notebook.version_info[0] < 7:
            extension_command = ["jupyter", "serverextension"]
    else:
        raise ValueError(
            f"backend_type must be 'jupyter-server' or 'jupyter-notebook' not {backend_type!r}"
        )

    # enable the extension
    subprocess.check_call(extension_command + ["enable", "nbgitpuller"], env=env)

    # launch the server
    jupyter_proc = subprocess.Popen(command, cwd=jupyterdir, env=env)
    wait_for_server()

    with jupyter_proc:
        yield jupyter_proc
        jupyter_proc.terminate()


def test_clone_default(jupyterdir, jupyter_server):
    """
    Tests use of 'repo' and 'branch' parameters.
    """
    with Remote() as remote, Pusher(remote) as pusher:
        pusher.push_file('README.md', 'Testing some content')
        print(f'path: {remote.path}')
        params = {
            'repo': remote.path,
            'branch': 'master',
        }
        r = request_api(params)
        assert r.code == 200
        s = r.read().decode()
        print(s)
        target_path = os.path.join(jupyterdir, os.path.basename(remote.path))
        assert '--branch master' in s
        assert f"Cloning into '{target_path}" in s
        assert os.path.isdir(os.path.join(target_path, '.git'))


def test_clone_auth(jupyterdir, jupyter_server):
    """
    Tests use of 'repo' and 'branch' parameters.
    """
    with Remote() as remote, Pusher(remote) as pusher:
        pusher.push_file('README.md', 'Testing some content')
        print(f'path: {remote.path}')
        params = {
            'repo': remote.path,
            'branch': 'master',
            'token': 'wrong',
        }
        r = request_api(params)
        # no token, redirect to login
        assert r.code == 403


def test_clone_targetpath(jupyterdir, jupyter_server):
    """
    Tests use of 'targetpath' parameter.
    """
    target = str(uuid4())
    with Remote() as remote, Pusher(remote) as pusher:
        pusher.push_file('README.md', 'Testing some content')
        params = {
            'repo': remote.path,
            'branch': 'master',
            'targetpath': target,
        }
        r = request_api(params)
        assert r.code == 200
        s = r.read().decode()
        print(s)
        target_path = os.path.join(jupyterdir, target)
        assert f"Cloning into '{target_path}" in s
        assert os.path.isdir(os.path.join(target_path, '.git'))


@pytest.mark.jupyter_server(extra_env={'NBGITPULLER_PARENTPATH': "parent"})
def test_clone_parenttargetpath(jupyterdir, jupyter_server):
    """
    Tests use of the NBGITPULLER_PARENTPATH environment variable.
    """
    parent = "parent"
    target = str(uuid4())

    with Remote() as remote, Pusher(remote) as pusher:
        pusher.push_file('README.md', 'Testing some content')
        params = {
            'repo': remote.path,
            'branch': 'master',
            'targetpath': target,
        }
        r = request_api(params)
        assert r.code == 200
        s = r.read().decode()
        print(s)
        target_path = os.path.join(jupyterdir, parent, target)
        assert f"Cloning into '{target_path}" in s
        assert os.path.isdir(os.path.join(target_path, '.git'))
