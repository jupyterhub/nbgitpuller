from tornado import gen, web
from gitautosync import GitAutoSync
from notebook.utils import url_path_join
from notebook.base.handlers import IPythonHandler
import threading
import json
import os
from queue import Queue, Empty
import jinja2


class SyncHandler(IPythonHandler):
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
        repo = self.get_argument('repo')
        branch = self.get_argument('branch')
        repo_dir = repo.split('/')[-1]

        # We gonna send out event streams!
        self.set_header('content-type', 'text/event-stream')
        self.set_header('cache-control', 'no-cache')

        gas = GitAutoSync(repo, branch, repo_dir)

        q = Queue()
        def pull():
            for line in gas.pull_from_remote():
                q.put_nowait(line)
            # Sentinel when we're done
            q.put_nowait(None)
        gas_thread = threading.Thread(target=pull)

        gas_thread.start()

        while True:
            try:
                progress = q.get_nowait()
            except Empty:
                yield gen.sleep(0.5)
                continue
            if progress is None:
                break

            self.emit({'output': progress, 'phase': 'Syncing'})

        self.emit({'phase': 'Finished'})

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
