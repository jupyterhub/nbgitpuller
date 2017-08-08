from .handlers import SyncHandler, UIHandler
from notebook.utils import url_path_join


def _jupyter_server_extension_paths():
    return [{
        'module': 'nbgitautosync',
    }]


def load_jupyter_server_extension(nbapp):
    web_app = nbapp.web_app
    handlers = [
        (url_path_join(web_app.settings['base_url'], 'sync-repo'), SyncHandler),
        (url_path_join(web_app.settings['base_url'], 'sync'), UIHandler)
    ]
    web_app.add_handlers('.*', handlers)
