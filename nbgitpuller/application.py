from .version import __version__ # noqa
from .pull import GitPuller # noqa
from jupyter_server.extension.application import ExtensionApp
from traitlets import Bool, CRegExp, List, Unicode, Union
from traitlets.config import Configurable
import os


class NbGitPuller(ExtensionApp):
    name = 'git-pull'
    load_other_extensions = True

    static_paths = [
        os.path.join(os.path.dirname(__file__), 'static')
    ]

    autorun_allow = Union(
        [Bool(), List(CRegExp())],
        default_value=False,
        config=True,
        help="""
        List of URLs described as Python regular expressions (using re.fullmatch()) where
        it is permitted to autorun scripts from the pulled project as a pre-initialisation
        step. Enable this only if you understand and accept the risks of AUTORUN.INF.

        When set to boolean True, all URLs are allowed, whilst False (default) autorun
        is disabled completely.
        """
    )

    autorun_script = List(
        Unicode(),
        default_value=[],
        config=True,
        help="""
        List of scripts to search for when attempting to autorun. The first match will
        be run with a single argument of 'init' or 'update' depending on what nbgitpuller
        is doing.

        Enable this only if you understand and accept the risks of AUTORUN.INF.
        """
    )

    def initialize_handlers(self):
        from .handlers import (
            SyncHandler,
            UIHandler,
            LegacyInteractRedirectHandler,
            LegacyGitSyncRedirectHandler,
        )

        # Extend the self.handlers trait
        self.handlers.extend([
            (rf'/{self.name}/api', SyncHandler),
            (rf'/{self.name}', UIHandler),
            (rf'/{self.name}/git-sync', LegacyGitSyncRedirectHandler),
            (rf'/{self.name}/interact', LegacyInteractRedirectHandler),
        ])
