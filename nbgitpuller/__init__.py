from .application import NbGitPuller


def _jupyter_server_extension_points():
    return [{
        'module': 'nbgitpuller',
        'app': NbGitPuller
    }]
