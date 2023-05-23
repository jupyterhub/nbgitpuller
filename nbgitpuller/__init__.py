from .version import __version__ # noqa
from .pull import GitPuller # noqa
from jupyter_server.utils import url_path_join
from tornado.web import StaticFileHandler
import os


def _jupyter_server_extension_points():
    """
    This function is detected by `notebook` and `jupyter_server` because they
    are explicitly configured to inspect the nbgitpuller module for it. That
    explicit configuration is passed via setup.py's declared data_files.

    Returns a list of dictionaries with metadata describing where to find the
    `_load_jupyter_server_extension` function.
    """
    return [{
        'module': 'nbgitpuller',
    }]


def _load_jupyter_server_extension(app):
    """
    This function is a hook for `notebook` and `jupyter_server` that we use to
    register additional endpoints to be handled by nbgitpuller.

    Note that as this function is used as a hook for both notebook and
    jupyter_server, the argument passed may be a NotebookApp or a ServerApp.

    Related documentation:
    - notebook: https://jupyter-notebook.readthedocs.io/en/stable/extending/handlers.htmland
    - notebook: https://jupyter-notebook.readthedocs.io/en/stable/examples/Notebook/Distributing%20Jupyter%20Extensions%20as%20Python%20Packages.html#Example---Server-extension
    - jupyter_server: https://jupyter-server.readthedocs.io/en/latest/developers/extensions.html
    """
    # identify base handler by app class
    # must do this before importing from .handlers
    from ._compat import get_base_handler

    get_base_handler(app)

    from .handlers import (
        SyncHandler,
        UIHandler,
        LegacyInteractRedirectHandler,
        LegacyGitSyncRedirectHandler,
    )

    web_app = app.web_app
    base_url = url_path_join(web_app.settings['base_url'], 'git-pull')
    handlers = [
        (url_path_join(base_url, 'api'), SyncHandler),
        (base_url, UIHandler),
        (url_path_join(web_app.settings['base_url'], 'git-sync'), LegacyGitSyncRedirectHandler),
        (url_path_join(web_app.settings['base_url'], 'interact'), LegacyInteractRedirectHandler),
        (
            url_path_join(base_url, 'static', '(.*)'),
            StaticFileHandler,
            {'path': os.path.join(os.path.dirname(__file__), 'static')}
        )
    ]
    # FIXME: See note on how to stop relying on settings to pass information:
    #        https://github.com/jupyterhub/nbgitpuller/pull/242#pullrequestreview-854968180
    #
    web_app.settings['nbapp'] = app
    web_app.add_handlers('.*', handlers)


# For compatibility with both notebook and jupyter_server, we define
# _jupyter_server_extension_paths alongside _jupyter_server_extension_points.
#
# "..._paths" is used by notebook and still supported by jupyter_server as of
# jupyter_server 1.13.3, but was renamed to "..._points" in jupyter_server
# 1.0.0.
#
_jupyter_server_extension_paths = _jupyter_server_extension_points

# For compatibility with both notebook and jupyter_server, we define both
# load_jupyter_server_extension alongside _load_jupyter_server_extension.
#
# "load..." is used by notebook and "_load..." is used by jupyter_server.
#
load_jupyter_server_extension = _load_jupyter_server_extension
