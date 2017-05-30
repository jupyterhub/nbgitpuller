import os


def construct_path(path, format, *args):
    """Constructs a path using locally available variables."""
    return os.path.join(path.format(**format), *args)
