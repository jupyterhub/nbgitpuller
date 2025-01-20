from .version import __version__ # noqa
from .pull import GitPuller # noqa
from jupyter_server.extension.application import ExtensionApp
import os


class NbGitPuller(ExtensionApp):
    name = 'git-pull'
    load_other_extensions = True

    static_paths = [
        os.path.join(os.path.dirname(__file__), 'static')
    ]

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
