from tornado import gen, web, locks
import traceback
import urllib.parse
from notebook.base.handlers import IPythonHandler
import threading
import json
import os
from queue import Queue, Empty
import jinja2

from .pull import GitPuller
from .version import __version__
from . import hookspecs
import pluggy


class ProviderException(Exception):
    """
    Custom Exception thrown when the provider key specifying
    the downloader plugin is not installed or can not be found by the
    name given
    """
    def __init__(self, response=None):
        self.response = response

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

    def setup_plugins(self, provider):
        pm = pluggy.PluginManager("nbgitpuller")
        pm.add_hookspecs(hookspecs)
        num_loaded =pm.load_setuptools_entrypoints("nbgitpuller", name=provider)
        if num_loaded == 0:
            raise ProviderException(f"The provider key you supplied in the URL could not be found: {provider}")
        return pm

    @gen.coroutine
    def progress_loop(self, queue):
        """
        The loop below constantly checks the queue paremeter for messages
        that are being sent to the UI so the user is kept aware of progress related to
        the downloading of archives and the merging of files into the user's home folder

        :param queue: This is either the download_queue or the original pull queue
        """
        while True:
            if queue.empty():
                yield gen.sleep(0.5)
                continue
            progress = queue.get_nowait()
            if progress is None:
                return
            if isinstance(progress, Exception):
                self.emit({
                    'phase': 'error',
                    'message': str(progress),
                    'output': '\n'.join([
                        line.strip()
                        for line in traceback.format_exception(
                            type(progress), progress, progress.__traceback__
                        )
                    ])
                })
                return

            self.emit({'output': progress, 'phase': 'syncing'})

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
            branch = self.get_argument('branch', None)
            provider = self.get_argument('provider', None)
            depth = self.get_argument('depth', None)
            if depth:
                depth = int(depth)
            # The default working directory is the directory from which Jupyter
            # server is launched, which is not the same as the root notebook
            # directory assuming either --notebook-dir= is used from the
            # command line or c.NotebookApp.notebook_dir is set in the jupyter
            # configuration. This line assures that all repos are cloned
            # relative to server_root_dir/<optional NBGITPULLER_PARENTPATH>,
            # so that all repos are always in scope after cloning. Sometimes
            # server_root_dir will include things like `~` and so the path
            # must be expanded.
            repo_parent_dir = os.path.join(os.path.expanduser(self.settings['server_root_dir']),
                                           os.getenv('NBGITPULLER_PARENTPATH', ''))
            repo_dir = os.path.join(repo_parent_dir, self.get_argument('targetpath', repo.split('/')[-1]))

            # We gonna send out event streams!
            self.set_header('content-type', 'text/event-stream')
            self.set_header('cache-control', 'no-cache')

            # if provider is specified then we are dealing with compressed
            # archive and not a git repo
            if provider is not None:
                pm = self.setup_plugins(provider)
                req_args = {k: v[0].decode() for k, v in self.request.arguments.items()}
                download_q = Queue()
                req_args["progress_func"] = lambda: self.progress_loop(download_q)
                req_args["download_q"] = download_q
                req_args["repo_parent_dir"] = repo_parent_dir
                hf_args = {"query_line_args": req_args}
                results = pm.hook.handle_files(**hf_args)
                repo_dir = repo_parent_dir + results["unzip_dir"]
                repo = "file://" + results["origin_repo_path"]

            gp = GitPuller(repo, repo_dir, branch=branch, depth=depth, parent=self.settings['nbapp'])
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
            self.progress_loop(q)
            yield gen.sleep(3)
            self.emit({'phase': 'finished'})

        except ProviderException as pe:
            self.emit({
                'phase': 'error',
                'message': str(pe),
                'output': '\n'.join([
                    line.strip()
                    for line in traceback.format_exception(
                        type(pe), pe, pe.__traceback__
                    )
                ])
        })
        except Exception as e:
            self.emit({
                'phase': 'error',
                'message': str(e),
                'output': '\n'.join([
                    line.strip()
                    for line in traceback.format_exception(
                        type(e), e, e.__traceback__
                    )
                ])
            })
        finally:
            self.git_lock.release()


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
        branch = self.get_argument('branch', None)
        depth = self.get_argument('depth', None)
        provider = self.get_argument('provider', None)
        urlPath = self.get_argument('urlpath', None) or \
                  self.get_argument('urlPath', None)
        subPath = self.get_argument('subpath', None) or \
                  self.get_argument('subPath', '.')
        app = self.get_argument('app', app_env)
        parent_reldir = os.getenv('NBGITPULLER_PARENTPATH', '')
        targetpath = self.get_argument('targetpath', None) or \
                     self.get_argument('targetPath', repo.split('/')[-1])

        if urlPath:
            path = urlPath
        else:
            path = os.path.join(parent_reldir, targetpath, subPath)
            if app.lower() == 'lab':
                path = 'lab/tree/' + path
            elif path.lower().endswith('.ipynb'):
                path = 'notebooks/' + path
            else:
                path = 'tree/' + path

        if provider is not None:
            path = "tree/"

        self.write(
            self.render_template(
                'status.html',
                repo=repo,
                branch=branch,
                path=path,
                depth=depth,
                provider=provider,
                targetpath=targetpath,
                version=__version__
            ))
        self.flush()


class LegacyGitSyncRedirectHandler(IPythonHandler):
    @web.authenticated
    @gen.coroutine
    def get(self):
        new_url = '{base}git-pull?{query}'.format(
            base=self.base_url,
            query=self.request.query
        )
        self.redirect(new_url)


class LegacyInteractRedirectHandler(IPythonHandler):
    @web.authenticated
    @gen.coroutine
    def get(self):
        repo = self.get_argument('repo')
        account = self.get_argument('account', 'data-8')
        repo_url = 'https://github.com/{account}/{repo}'.format(account=account, repo=repo)
        query = {
            'repo': repo_url,
            # branch & subPath are optional
            'branch': self.get_argument('branch', 'gh-pages'),
            'subPath': self.get_argument('path', '.')
        }
        new_url = '{base}git-pull?{query}'.format(
            base=self.base_url,
            query=urllib.parse.urlencode(query)
        )

        self.redirect(new_url)


class ThreadWithResult(threading.Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}, *, daemon=None):
        def function():
            self.result = target(*args, **kwargs)
        super().__init__(group=group, target=function, name=name, daemon=daemon)
