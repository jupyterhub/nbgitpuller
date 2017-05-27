import os
import shutil
import logging

"""
Format for downloading zip files of Git folders

:param repo: the repository name, from the Data8 organization on Github
:param path: path to the desired file or folder
"""
GIT_DOWNLOAD_LINK_FORMAT = 'https://minhaskamal.github.io/DownGit/#/home?url' \
                           '=http://github.com/data-8/{repo}/tree/gh-pages/{' \
                           'path}'


# Log all messages by default
logging.basicConfig(
    format='[%(asctime)s] %(levelname)s -- %(message)s',
    level=logging.DEBUG)
logger = logging.getLogger('app')


def chown(path, filename):
    """Set owner and group of file to that of the parent directory."""
    s = os.stat(path)
    os.chown(os.path.join(path, filename), s.st_uid, s.st_gid)


def chown_dir(directory, username):
    """Set owner and group of directory to username."""
    shutil.chown(directory, username, username)
    for root, dirs, files in os.walk(directory):
        for child in dirs + files:
            shutil.chown(os.path.join(root, child), username, username)
    logger.info("{} chown'd to {}".format(directory, username))


def construct_path(path, format, *args):
    """Constructs a path using locally available variables."""
    return os.path.join(path.format(**format), *args)


def generate_git_download_link(args):
    """ DEPRECATED! SHOULD NOT BE USED DUE TO WRONG
    BRANCH NAME.
    Generates a download link for files hosted on Git.

    :param args: dictionary of query string "arguments"
    :return: URIs for the specified git resources
    """
    return [GIT_DOWNLOAD_LINK_FORMAT.format(
        repo=args['repo'],
        path=path) for path in args['path']]
