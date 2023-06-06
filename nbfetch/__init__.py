from .version import __version__
from .handlers import HSLoginHandler, SyncHandler, HSyncHandler, UIHandler, HSHandler
from notebook.utils import url_path_join
from tornado.web import StaticFileHandler
import os

import jupyter_server
from jupyter_server.extension.application import ExtensionApp
from notebook import DEFAULT_STATIC_FILES_PATH, DEFAULT_TEMPLATE_PATH_LIST
import jinja2
import gettext


HERE = os.path.dirname(__file__)


class NbFetchApp(ExtensionApp):
    # Name of the extension.
    name = "nbfetch"
    default_url = "/nbfetch"
    load_other_extensions = True
    file_url_prefix = "/"

    # Local path to static files directory.
    static_paths = [
        os.path.join(HERE, "static"),
        DEFAULT_STATIC_FILES_PATH,
    ]

    def initialize_templates(self):
        template_paths = [os.path.join(HERE, "templates"), *DEFAULT_TEMPLATE_PATH_LIST]

        self.settings.update({f"{self.name}_template_paths": template_paths})

        self.jinja2_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(template_paths),
            extensions=["jinja2.ext.i18n"],
            autoescape=True,
        )

        base_dir = os.path.realpath(os.path.join(jupyter_server.__file__, "..", ".."))
        nbui = gettext.translation(
            "nbui",
            localedir=os.path.join(base_dir, "jupyter_server/i18n"),
            fallback=True,
        )

        self.jinja2_env.install_gettext_translations(nbui, newstyle=False)

        # Add the jinja2 environment for this extension to the tornado settings.
        self.settings.update({f"{self.name}_jinja2_env": self.jinja2_env})

    def initialize_handlers(self):
        # Add a group with () to send to handler.
        base_url = r"/nbfetch"
        git_url = url_path_join(base_url, "git-pull")
        hs_url = url_path_join(base_url, "hs-pull")

        self.handlers.extend(
            [
                (url_path_join(git_url, "api"), SyncHandler),
                (url_path_join(hs_url, "api"), HSyncHandler),
                (git_url, UIHandler),
                (hs_url, HSHandler),
                (
                    url_path_join(git_url, "static", "(.*)"),
                    StaticFileHandler,
                    {"path": os.path.join(HERE, "static")},
                ),
                (
                    url_path_join(hs_url, "static", "(.*)"),
                    StaticFileHandler,
                    {"path": os.path.join(HERE, "static")},
                ),
                (
                    url_path_join(base_url, "hslogin"),
                    HSLoginHandler,
                ),
            ]
        )

def _jupyter_server_extension_points():
    """
    This function is detected by `notebook` and `jupyter_server` because they
    are explicitly configured to inspect the nbgitpuller module for it. That
    explicit configuration is passed via setup.py's declared data_files.

    Returns a list of dictionaries with metadata describing where to find the
    `_load_jupyter_server_extension` function.
    """
    return [{
        "module": "nbfetch", "app": NbFetchApp,
    }]


def _load_jupyter_server_extension(app):
    """
    This function is a hook for `notebook` and `jupyter_server` that we use to
    register additional endpoints to be handled by nbfetch.

    Note that as this function is used as a hook for both notebook and
    jupyter_server, the argument passed may be a NotebookApp or a ServerApp.

    Related documentation:
    - notebook: https://jupyter-notebook.readthedocs.io/en/stable/extending/handlers.htmland
    - notebook: https://jupyter-notebook.readthedocs.io/en/stable/examples/Notebook/Distributing%20Jupyter%20Extensions%20as%20Python%20Packages.html#Example---Server-extension
    - jupyter_server: https://jupyter-server.readthedocs.io/en/latest/developers/extensions.html
    """
    web_app = app.web_app
    base_url = url_path_join(web_app.settings['base_url'], 'nbfetch')
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

# TODO: DRC 06.06.23 hope we can get away without this...
# load_jupyter_server_extension = _load_jupyter_server_extension
