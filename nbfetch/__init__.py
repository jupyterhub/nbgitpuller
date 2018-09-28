from .version import __version__
from .handlers import HSLoginHandler, SyncHandler, HSyncHandler, UIHandler, HSHandler
from .pull import GitPuller
from notebook.utils import url_path_join
from tornado.web import StaticFileHandler
import os


def _jupyter_server_extension_paths():
    return [{
        'module': 'nbfetch',
    }]


def load_jupyter_server_extension(nbapp):
    web_app = nbapp.web_app
    base_url = url_path_join(web_app.settings['base_url'], 'git-pull')
    hs_url = url_path_join(web_app.settings['base_url'], 'hs-pull')
    handlers = [
        (url_path_join(base_url, 'api'), SyncHandler),
        (url_path_join(hs_url, 'api'), HSyncHandler),
        (base_url, UIHandler),
        (hs_url, HSHandler),
        (
            url_path_join(base_url, 'static', '(.*)'),
            StaticFileHandler,
            {'path': os.path.join(os.path.dirname(__file__), 'static')}
        ),
        (
            url_path_join(hs_url, 'static', '(.*)'),
            StaticFileHandler,
            {'path': os.path.join(os.path.dirname(__file__), 'static')}
        ),
        (url_path_join(web_app.settings['base_url'], 'hslogin'), HSLoginHandler),
    ]
    web_app.add_handlers('.*', handlers)
