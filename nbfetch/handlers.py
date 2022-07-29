from tornado import gen, web, locks
from tornado.escape import url_escape, url_unescape
import traceback
from urllib.parse import urljoin

import threading
import json
import os
from pathlib import Path
import io
from queue import Queue, Empty
from hs_restclient import HydroShare, HydroShareAuthBasic, HydroShareAuthOAuth2
from .pull import GitPuller, HSPuller
from .version import __version__
import pickle
from jupyter_server.base.handlers import JupyterHandler
from jupyter_server.extension.handler import (
    ExtensionHandlerMixin,
    ExtensionHandlerJinjaMixin,
)

# typing imports
from typing import Optional, Tuple


class ExtensionHandler(
    ExtensionHandlerMixin, ExtensionHandlerJinjaMixin, JupyterHandler
):
    @property
    def app_url(self) -> str:
        """Base url joined to extension name.

        If `jupyter_server.extension.application.ExtensionApp` not used to configure extension, it
        is possible that `self.name` is "".
        """
        return urljoin(self.base_url, "{}/".format(self.name))


class HSLoginHandler(ExtensionHandler):
    @gen.coroutine
    def get(self):
        self.log.info("LOGIN GET" + self.request.uri)
        params = {
            "hslogin": urljoin(self.request.uri, "hslogin"),
            "image": urljoin(self.request.uri, "hs-pull/static/hydroshare_logo.png"),
            "error": self.get_argument("error", "Login Needed"),
            "next": self.get_argument("next", "/"),
        }
        temp = self.render_template("hslogin.html", **params)
        self.write(temp)

    @gen.coroutine
    def post(self):
        pwfile = os.path.expanduser("~/.hs_pass")
        userfile = os.path.expanduser("~/.hs_user")
        with open(userfile, "w") as f:
            f.write(self.get_argument("name"))
        with open(pwfile, "w") as f:
            f.write(self.get_argument("pass"))
        self.redirect(url_unescape(self.get_argument("next", "/")))


class SyncHandler(ExtensionHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # We use this lock to make sure that only one sync operation
        # can be happening at a time. Git doesn't like concurrent use!
        if "git_lock" not in self.settings:
            self.settings["git_lock"] = locks.Lock()

    @property
    def git_lock(self):
        return self.settings["git_lock"]

    @gen.coroutine
    def emit(self, data):
        if type(data) is not str:
            serialized_data = json.dumps(data)
            if "output" in data:
                self.log.info(data["output"].rstrip())
        else:
            serialized_data = data
            self.log.info(data)
        self.write("data: {}\n\n".format(serialized_data))
        yield self.flush()

    @web.authenticated
    @gen.coroutine
    def get(self):
        try:
            yield self.git_lock.acquire(1)
        except gen.TimeoutError:
            self.emit(
                {
                    "phase": "error",
                    "message": "Another git operations is currently running, try again in a few minutes",
                }
            )
            return

        try:
            repo = self.get_argument("repo")
            branch = self.get_argument("branch")
            repo_dir = repo.split("/")[-1]

            # We gonna send out event streams!
            self.set_header("content-type", "text/event-stream")
            self.set_header("cache-control", "no-cache")

            gp = GitPuller(repo, branch, repo_dir)

            q = Queue()

            def pull():
                try:
                    for line in gp.pull():
                        q.put_nowait(line)
                    # Sentinel when we're done
                    q.put_nowait(None)
                except Exception as e:
                    q.put_nowait(e)
                    raise e

            self.gp_thread = threading.Thread(target=pull)

            self.gp_thread.start()

            while True:
                try:
                    progress = q.get_nowait()
                except Empty:
                    yield gen.sleep(0.5)
                    continue
                if progress is None:
                    break
                if isinstance(progress, Exception):
                    self.emit(
                        {
                            "phase": "error",
                            "message": str(progress),
                            "output": "\n".join(
                                [
                                    l.strip()
                                    for l in traceback.format_exception(
                                        type(progress), progress, progress.__traceback__
                                    )
                                ]
                            ),
                        }
                    )
                    return

                self.emit({"output": progress, "phase": "syncing"})

            self.emit({"phase": "finished"})
        except Exception as e:
            self.emit(
                {
                    "phase": "error",
                    "message": str(e),
                    "output": "\n".join(
                        [
                            l.strip()
                            for l in traceback.format_exception(
                                type(e), e, e.__traceback__
                            )
                        ]
                    ),
                }
            )
        finally:
            self.git_lock.release()


class HSyncHandler(ExtensionHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.log.info("HSyncHandler")

    @gen.coroutine
    def emit(self, data):
        if type(data) is not str:
            serialized_data = json.dumps(data)
            if "output" in data:
                self.log.info(data["output"].rstrip())
        else:
            serialized_data = data
            self.log.info(data)
        self.write("data: {}\n\n".format(serialized_data))
        yield self.flush()

    @gen.coroutine
    def post(self):
        print(self.get_argument("email"), self.get_argument("name"))
        print("id=", self.get_argument("id"))

    # @web.authenticated
    @gen.coroutine
    def get(self):
        try:
            id = self.get_argument("id")

            # We gonna send out event streams!
            self.set_header("content-type", "text/event-stream")
            self.set_header("cache-control", "no-cache")

            hs = HSPuller(id, self.settings["hydroshare"])

            q = Queue()

            def pull():
                try:
                    for line in hs.pull():
                        q.put_nowait(line)
                    # Sentinel when we're done
                    q.put_nowait(None)
                except Exception as e:
                    q.put_nowait(e)
                    raise e

            self.hs_thread = threading.Thread(target=pull)

            self.hs_thread.start()

            while True:
                try:
                    progress = q.get_nowait()
                except Empty:
                    yield gen.sleep(0.5)
                    continue
                if progress is None:
                    break
                if isinstance(progress, Exception):
                    self.emit(
                        {
                            "phase": "error",
                            "message": str(progress),
                            "output": "\n".join(
                                [
                                    l.strip()
                                    for l in traceback.format_exception(
                                        type(progress), progress, progress.__traceback__
                                    )
                                ]
                            ),
                        }
                    )
                    return

                self.emit({"output": progress, "phase": "syncing"})

            self.emit({"phase": "finished"})
        except Exception as e:
            self.emit(
                {
                    "phase": "error",
                    "message": str(e),
                    "output": "\n".join(
                        [
                            l.strip()
                            for l in traceback.format_exception(
                                type(e), e, e.__traceback__
                            )
                        ]
                    ),
                }
            )


class UIHandler(ExtensionHandler):
    @web.authenticated
    @gen.coroutine
    def get(self):
        app_env = os.getenv("NBGITPULLER_APP", default="notebook")

        repo = self.get_argument("repo")
        branch = self.get_argument("branch", "master")
        urlPath = self.get_argument("urlpath", None) or self.get_argument(
            "urlPath", None
        )
        subPath = self.get_argument("subpath", None) or self.get_argument(
            "subPath", "."
        )
        app = self.get_argument("app", app_env)

        if urlPath:
            path = urlPath
        else:
            repo_dir = repo.split("/")[-1]
            path = os.path.join(repo_dir, subPath)
            if app.lower() == "lab":
                path = "lab/tree/" + path
            elif path.lower().endswith(".ipynb"):
                path = "notebooks/" + path
            else:
                path = "tree/" + path

        self.write(
            self.render_template(
                "status.html", repo=repo, branch=branch, path=path, version=__version__
            )
        )
        self.flush()


class HSHandler(ExtensionHandler):
    def check_auth(self, auth):
        hs = HydroShare(auth=auth)
        self.log.info("hs=%s" % str(hs))

        try:
            info = hs.getUserInfo()
            self.settings["hydroshare"] = hs
            self.log.info("info=%s" % info)
        except:
            hs = None
        return hs

    def login(self):
        hs = None

        # check for oauth
        authfile = os.path.expanduser("~/.hs_auth")
        try:
            with open(authfile, "rb") as f:
                token, cid = pickle.load(f)
            auth = HydroShareAuthOAuth2(cid, "", token=token)
            self.log.info("auth=%s" % str(auth))

            hs = self.check_auth(auth)
            self.log.info("hs=%s" % str(hs))

            if hs is None:
                message = url_escape(
                    "Oauth Login Failed.  Login with username and password or logout from JupyterHub and reauthenticate with Hydroshare."
                )
        except:
            message = ""

        if hs is None:
            # If oauth fails, we can log in using
            # user name and password.  These are saved in
            # files in the home directory.
            username, password = _get_user_authentication()
            try:
                auth = HydroShareAuthBasic(username=username, password=password)
                hs = self.check_auth(auth)
                if hs is None:
                    message = url_escape("Login Failed. Please Try again")
            except:
                message = url_escape(
                    "You need to provide login credentials to access HydroShare Resources."
                )

        if hs is None:
            _next = url_escape(url_escape(self.request.uri))
            upath = urljoin(self.request.uri, "hslogin")
            self.redirect("%s?error=%s&next=%s" % (upath, message, _next))

    @web.authenticated
    @gen.coroutine
    def get(self):
        """
        Get or go to the required resource. Parameters:
        id - Resource id (required)
        start - notebook to launch (optional)
        app - Optinal. 'lab' will try to run jupyter lab
        overwrite - Overwrite any existing local copy or the resource
        goto - Do not overwrite.  Just go to the resouce
        """

        app_env = "notebook"
        self.log.info("HS GET " + str(self.request.uri))

        self.login()

        id = self.get_argument("id")
        start = self.get_argument("start", "")
        app = self.get_argument("app", app_env)
        overwrite = self.get_argument("overwrite", 0)
        goto = self.get_argument("goto", 0)

        self.log.info("GET %s %s %s %s %s" % (id, start, app, overwrite, goto))

        # create Downloads directory if necessary
        download_dir = os.environ.get("JUPYTER_DOWNLOADS", "Downloads")
        if not os.path.isdir(download_dir):
            os.makedirs(download_dir)

        nbdir = os.environ.get("NOTEBOOK_HOME")
        relative_download_dir = os.path.relpath(download_dir, nbdir)
        pathid = os.path.join(relative_download_dir, id)
        if os.path.exists(pathid) and goto == 0 and overwrite == 0:
            # overwrite or not? display modal dialog
            self.write(self.render_template("confirm.html", directory=pathid))
            self.flush()
            return

        path = os.path.join(pathid, id, "data", "contents", start)
        if app.lower() == "lab":
            path = "lab/tree/" + path
        elif path.lower().endswith(".ipynb"):
            path = "notebooks/" + path
        else:
            path = "tree/" + path

        self.log.info("path=%s" % path)
        if goto:
            self.redirect(path)
            return

        self.write(
            self.render_template("hstatus.html", id=id, path=path, version=__version__)
        )
        self.flush()


def _get_user_authentication() -> Tuple[Optional[str], Optional[str]]:
    """retrieve HS authentication from standard locations(see below) as tuple of username and
    password. If either cannot be located, both tuple members are be None.

    Note: files take precedence over environment variables
    standard file locations:
        `~/.hs_user`
        `~/.hs_pass`
    standard environment variables:
        `HS_USER`
        `HS_PASS`

    Returns
    -------
    Tuple[Optional[str], Optional[str]]
        username, password
    """
    userfile = Path("~/.hs_user").expanduser()
    pwfile = Path("~/.hs_pass").expanduser()

    user = (
        userfile.read_text().strip()
        if userfile.exists()
        else os.getenv("HS_USER", None)
    )

    pw = pwfile.read_text().strip() if pwfile.exists() else os.getenv("HS_PASS", None)

    return user, pw
