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

from nbgitpuller import hookspecs
import pluggy




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
        print("SyncHandler get")
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

            """
            Check type of FMS, if third party, account for repo_dir changes
            """

            fms = self.hook.check_fms(type=self.get_argument('type'))

            if (fms):
                print("fms is true")
                is_new = self.hook.is_new_assignment(repo_parent_dir=repo_parent_dir, repo_dir=repo_dir)
                if (is_new) :
                    print("is_new")
                    repo_dir = is_new





            # We gonna send out event streams!
            self.set_header('content-type', 'text/event-stream')
            self.set_header('cache-control', 'no-cache')

            """
            Before we initialize gitpuller, we must either create a remote git repository
            with our third party file managment system's notebook files or update
            the already existing one with the most recent version in the FMS
            """



            if (fms):

                results = self.hook.sync_file_management_system(
                    repo=repo,
                    parent_dir=repo_parent_dir,
                    repo_dir=repo_dir
                )
                print(results)






            gp = GitPuller(repo, branch, repo_dir, depth=depth, parent=self.settings['nbapp'])

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
                            line.strip()
                            for line in traceback.format_exception(
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
        print("UIHandler get")

        app_env = os.getenv('NBGITPULLER_APP', default='notebook')

        repo = self.get_argument('repo')
        branch = self.get_argument('branch', 'master')
        depth = self.get_argument('depth', None)
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

        self.write(
            self.render_template(
                'status.html',
                repo=repo, branch=branch, path=path, depth=depth, targetpath=targetpath, version=__version__
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
