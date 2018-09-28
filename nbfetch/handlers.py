from tornado import gen, web, locks
from tornado.escape import url_escape, url_unescape
import traceback
from urllib.parse import urljoin
from notebook.base.handlers import IPythonHandler
import threading
import json
import os
from queue import Queue, Empty
import jinja2
from hs_restclient import HydroShare, HydroShareAuthBasic, HydroShareAuthOAuth2
from .pull import GitPuller, HSPuller
from .version import __version__
from notebook.utils import url_path_join

#https://gist.github.com/guillaumevincent/4771570

class HSLoginHandler(IPythonHandler):
    @gen.coroutine
    def get(self):
        self.log.info('LOGIN GET' + self.request.uri)
        params = {
            "hslogin": urljoin(self.request.uri, 'hslogin'),
            "image": urljoin(self.request.uri, 'hs-pull/static/hydroshare_logo.png'),
            "error": self.get_argument("error",'Login Needed'),
            "next": self.get_argument("next", "/")
        }
        temp = self.render_template("hslogin.html", **params)
        self.write(temp)

    @gen.coroutine
    def post(self):
        pwfile = os.path.expanduser("~/.hs_pass")
        userfile = os.path.expanduser("~/.hs_user")
        with open(userfile, 'w') as f:
            f.write(self.get_argument("name"))
        with open(pwfile, 'w') as f:
            f.write(self.get_argument("pass"))
        self.redirect(url_unescape(self.get_argument("next", "/")))


class SyncHandler(IPythonHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # We use this lock to make sure that only one sync operation
        # can be happening at a time. Git doesn't like concurrent use!
        if 'git_lock' not in self.settings:
            self.settings['git_lock'] = locks.Lock()

    @property
    def git_lock(self):
        return self.settings['git_lock']

    @gen.coroutine
    def emit(self, data):
        if type(data) is not str:
            serialized_data = json.dumps(data)
            if 'output' in data:
                self.log.info(data['output'].rstrip())
        else:
            serialized_data = data
            self.log.info(data)
        self.write('data: {}\n\n'.format(serialized_data))
        yield self.flush()

    @web.authenticated
    @gen.coroutine
    def get(self):
        try:
            yield self.git_lock.acquire(1)
        except gen.TimeoutError:
            self.emit({
                'phase': 'error',
                'message': 'Another git operations is currently running, try again in a few minutes'
            })
            return

        try:
            repo = self.get_argument('repo')
            branch = self.get_argument('branch')
            repo_dir = repo.split('/')[-1]

            # We gonna send out event streams!
            self.set_header('content-type', 'text/event-stream')
            self.set_header('cache-control', 'no-cache')

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
                    self.emit({
                        'phase': 'error',
                        'message': str(progress),
                        'output': '\n'.join([
                            l.strip()
                            for l in traceback.format_exception(
                                type(progress), progress, progress.__traceback__
                            )
                        ])
                    })
                    return

                self.emit({'output': progress, 'phase': 'syncing'})

            self.emit({'phase': 'finished'})
        except Exception as e:
            self.emit({
                'phase': 'error',
                'message': str(e),
                'output': '\n'.join([
                    l.strip()
                    for l in traceback.format_exception(
                        type(e), e, e.__traceback__
                    )
                ])
            })
        finally:
            self.git_lock.release()


class HSyncHandler(IPythonHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.log.info("HSyncHandler")

    @gen.coroutine
    def emit(self, data):
        if type(data) is not str:
            serialized_data = json.dumps(data)
            if 'output' in data:
                self.log.info(data['output'].rstrip())
        else:
            serialized_data = data
            self.log.info(data)
        self.write('data: {}\n\n'.format(serialized_data))
        yield self.flush()


    @gen.coroutine
    def post(self):
        print(self.get_argument("email"), self.get_argument("name"))
        print('id=', self.get_argument('id'))


    # @web.authenticated
    @gen.coroutine
    def get(self):
        self.log.info("HSYNC GET")

        try:
            id = self.get_argument('id')

            # We gonna send out event streams!
            self.set_header('content-type', 'text/event-stream')
            self.set_header('cache-control', 'no-cache')

            hs = HSPuller(id, self.settings['hydroshare'])

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
                    self.emit({
                        'phase': 'error',
                        'message': str(progress),
                        'output': '\n'.join([
                            l.strip()
                            for l in traceback.format_exception(
                                type(progress), progress, progress.__traceback__
                            )
                        ])
                    })
                    return

                self.emit({'output': progress, 'phase': 'syncing'})

            self.emit({'phase': 'finished'})
        except Exception as e:
            self.emit({
                'phase': 'error',
                'message': str(e),
                'output': '\n'.join([
                    l.strip()
                    for l in traceback.format_exception(
                        type(e), e, e.__traceback__
                    )
                ])
            })
        

class UIHandler(IPythonHandler):
    def initialize(self):
        super().initialize()
        # FIXME: Is this really the best way to use jinja2 here?
        # I can't seem to get the jinja2 env in the base handler to
        # actually load templates from arbitrary paths ugh.
        jinja2_env = self.settings['jinja2_env']
        jinja2_env.loader = jinja2.ChoiceLoader([
            jinja2_env.loader,
            jinja2.FileSystemLoader(
                os.path.join(os.path.dirname(__file__), 'templates')
            )
        ])

    @web.authenticated
    @gen.coroutine
    def get(self):
        app_env = os.getenv('NBGITPULLER_APP', default='notebook')

        repo = self.get_argument('repo')
        branch = self.get_argument('branch', 'master')
        urlPath = self.get_argument('urlpath', None) or \
                  self.get_argument('urlPath', None)
        subPath = self.get_argument('subpath', None) or \
                  self.get_argument('subPath', '.')
        app = self.get_argument('app', app_env)

        if urlPath:
            path = urlPath
        else:
            repo_dir = repo.split('/')[-1]
            path = os.path.join(repo_dir, subPath)
            if app.lower() == 'lab':
                path = 'lab/tree/' + path
            elif path.lower().endswith('.ipynb'):
                path = 'notebooks/' + path
            else:
                path = 'tree/' + path

        self.write(
            self.render_template(
                'status.html',
                repo=repo, branch=branch, path=path, version=__version__
            ))
        self.flush()

class HSHandler(IPythonHandler):
    def initialize(self):
        super().initialize()
        jinja2_env = self.settings['jinja2_env']
        jinja2_env.loader = jinja2.ChoiceLoader([
            jinja2_env.loader,
            jinja2.FileSystemLoader(
                os.path.join(os.path.dirname(__file__), 'templates')
            )
        ])

    @web.authenticated
    @gen.coroutine
    def get(self):
        app_env = 'notebook'
        self.log.info('HS GET ' + str(self.request.uri))

        # look for these files.  If they exist, 
        # try to log in with their contents
        pwfile = os.path.expanduser("~/.hs_pass")
        userfile = os.path.expanduser("~/.hs_user")

        needs_login = False
        login_error = False

        try:
            with open(userfile) as f:
                username = f.read().strip()
            with open(pwfile) as f:
                password = f.read().strip()
            auth = HydroShareAuthBasic(username=username, password=password)
            hs = HydroShare(auth=auth)
            try:
                info = hs.getUserInfo()
                self.settings['hydroshare'] = hs
                self.log.info('info=%s' % info)
            except:
                login_error = True
        except:
            needs_login = True

        if needs_login or login_error:
            if login_error:
                message = url_escape("Login Failed. Please Try again")
            else:
                message = url_escape("You need to provide login credentials to access HydroShare Resources.")
            _next = url_escape(url_escape(self.request.uri))
            upath = urljoin(self.request.uri, 'hslogin')
            self.redirect('%s?error=%s&next=%s' % (upath, message, _next))
            return

        id = self.get_argument('id')
        urlPath = self.get_argument('urlpath', None) or \
                  self.get_argument('urlPath', None)
        start = self.get_argument('start', '')
        app = self.get_argument('app', app_env)

        # FIXME: We always overwrite.  Should probably have a dialog before doing that.
        if urlPath:
            path = urlPath
        else:
            path = os.path.join(id, id, 'data', 'contents', start)
            if app.lower() == 'lab':
                path = 'lab/tree/' + path
            elif path.lower().endswith('.ipynb'):
                path = 'notebooks/' + path
            else:
                path = 'tree/' + path

        self.log.info('path=%s' % path)

        self.write(
            self.render_template(
                'hstatus.html',
                id=id, path=path, version=__version__
            ))
        self.flush()
