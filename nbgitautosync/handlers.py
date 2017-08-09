from tornado import gen, web, locks
import traceback

from gitautosync import GitAutoSync
from notebook.utils import url_path_join
from notebook.base.handlers import IPythonHandler
import threading
import json
import os
from queue import Queue, Empty
import jinja2


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
        else:
            serialized_data = data
        self.write('data: {}\n\n'.format(serialized_data))
        yield self.flush()

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

            gas = GitAutoSync(repo, branch, repo_dir)

            q = Queue()
            def pull():
                try:
                    for line in gas.pull_from_remote():
                        q.put_nowait(line)
                    # Sentinel when we're done
                    q.put_nowait(None)
                except Exception as e:
                    q.put_nowait(e)
                    raise e
            self.gas_thread = threading.Thread(target=pull)

            self.gas_thread.start()

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

    @gen.coroutine
    def get(self):
        repo = self.get_argument('repo')
        subPath = self.get_argument('subPath', '.')
        branch = self.get_argument('branch', 'master')

        repo_dir = repo.split('/')[-1]
        path = os.path.join(repo_dir, subPath)

        self.write(
            self.render_template(
                'nbgitautosync.html',
                repo=repo, path=path, branch=branch
            ))
        self.flush()
