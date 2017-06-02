import os
import subprocess
from .util import logger


def pull_from_remote(git_url, branch_name, repo_dir):
    """
    Pull selected repo from a remote git repository,
    while preserving user changes
    """
    assert git_url and branch_name

    logger.info('Starting pull.')
    logger.info('    Git Url: {}'.format(git_url))
    logger.info('    Branch: {}'.format(branch_name))
    logger.info('    Repo Dir: {}'.format(repo_dir))

    if not os.path.exists(repo_dir):
        _initialize_repo(git_url, repo_dir)
    else:
        _make_commit_if_dirty(repo_dir, branch_name)
        _pull_and_resolve_conflicts(git_url, repo_dir, branch_name)

    logger.info('Pulled from repo: {}'.format(git_url))


def _initialize_repo(git_url, repo_dir):
    """
    Clones repository.
    """
    logger.info('Repo {} doesn\'t exist. Cloning...'.format(repo_dir))

    # Clone repo
    subprocess.check_call(['git', 'clone', git_url, repo_dir])

    logger.info('Repo {} initialized'.format(repo_dir))


def _make_commit_if_dirty(repo_dir, branch_name):
    """
    Makes a commit with message 'WIP' if there are changes.
    """
    cwd = _get_sub_cwd(repo_dir)
    if _repo_is_dirty(repo_dir):
        subprocess.check_call(['git', 'checkout', branch_name], cwd=cwd)
        subprocess.check_call(['git', 'add', '-A'], cwd=cwd)
        subprocess.check_call(['git', 'commit', '-m', 'WIP'], cwd=cwd)
        logger.info('Made WIP commit')


def _pull_and_resolve_conflicts(git_url, repo_dir, branch_name):
    """
    Git pulls, resolving conflicts with -Xours
    """
    logger.info('Starting pull from {}'.format(git_url))

    # Fetch then merge, resolving conflicts by keeping original content
    cwd = _get_sub_cwd(repo_dir)
    subprocess.check_call(['git', 'checkout', branch_name], cwd=cwd)
    subprocess.check_call(['git', 'fetch'], cwd=cwd)
    subprocess.check_call(['git', 'merge', '-Xours', 'origin/{}'.format(branch_name)], cwd=cwd)

    logger.info('Pulled from {}'.format(git_url))


def _repo_is_dirty(repo_dir):
    cwd = _get_sub_cwd(repo_dir)
    out = subprocess.check_output(['git', 'diff-index', '--name-only', 'HEAD', '--'], cwd=cwd)
    return out


def _get_sub_cwd(repo_dir):
    return '{}/{}'.format(os.getcwd(), repo_dir)
