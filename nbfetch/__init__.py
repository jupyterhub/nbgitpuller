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


def _jupyter_server_extension_paths():
    return [{"module": "nbfetch", "app": NbFetchApp}]
