from tornado import gen, web, locks
import traceback
import urllib.parse

import threading
import json
import os
from queue import Queue, Empty
import jinja2

from .pull import GitPuller
from .version import __version__
from ._compat import get_base_handler

JupyterHandler = get_base_handler()


jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(
        os.path.join(os.path.dirname(__file__), 'templates')
    ),
)

class SyncHandler(JupyterHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # We use this lock to make sure that only one sync operation
        # can be happening at a time. Git doesn't like concurrent use!
        if 'git_lock' not in self.settings:
            self.settings['git_lock'] = locks.Lock()

    def get_login_url(self):
        # raise on failed auth, not redirect
        # can't redirect EventStream to login
        # same as Jupyter's APIHandler
        raise web.HTTPError(403)

    @property
    def git_lock(self):
        return self.settings['git_lock']

    async def emit(self, data):
        if type(data) is not str:
            serialized_data = json.dumps(data)
            if 'output' in data:
                self.log.info(data['output'].rstrip())
        else:
            serialized_data = data
            self.log.info(data)
        self.write('data: {}\n\n'.format(serialized_data))
        await self.flush()

    @web.authenticated
    async def get(self):
        try:
            await self.git_lock.acquire(1)
        except gen.TimeoutError:
            await self.emit({
                'phase': 'error',
                'message': 'Another git operations is currently running, try again in a few minutes'
            })
            return

        try:
            repo = self.get_argument('repo')
            branch = self.get_argument('branch', None)
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

            while True:
                try:
                    progress = q.get_nowait()
                except Empty:
                    await gen.sleep(0.5)
                    continue
                if progress is None:
                    break
                if isinstance(progress, Exception):
                    await self.emit({
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

                await self.emit({'output': progress, 'phase': 'syncing'})

            await self.emit({'phase': 'finished'})
        except Exception as e:
            await self.emit({
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


class UIHandler(JupyterHandler):
    @web.authenticated
    async def get(self):
        app_env = os.getenv('NBGITPULLER_APP', default='notebook')

        repo = self.get_argument('repo')
        branch = self.get_argument('branch', None)
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
            jinja_env.get_template('status.html').render(
                repo=repo, branch=branch, path=path, depth=depth, targetpath=targetpath, version=__version__,
                **self.template_namespace
            )
        )
        await self.flush()


class LegacyGitSyncRedirectHandler(JupyterHandler):
    """
    The /git-pull endpoint was previously exposed /git-sync.

    For backward compatibility we keep listening to the /git-sync endpoint but
    respond with a redirect to the /git-pull endpoint.
    """
    @web.authenticated
    async def get(self):
        new_url = '{base}git-pull?{query}'.format(
            base=self.base_url,
            query=self.request.query
        )
        self.redirect(new_url)


class LegacyInteractRedirectHandler(JupyterHandler):
    """
    The /git-pull endpoint was previously exposed /interact.

    For backward compatibility we keep listening to the /interact endpoint but
    respond with a redirect to the /git-pull endpoint.
    """
    @web.authenticated
    async def get(self):
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
