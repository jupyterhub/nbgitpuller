import os
import re
import json
import click
import git
import errno
from . import util


def pull_from_remote(repo_name, branch_name, config_file_name, sync_path, account, domain):
    assert repo_name and branch_name and config_file_name

    click.echo('Starting pull.')
    click.echo('    Domain: {}'.format(domain))
    click.echo('    Repo: {}'.format(repo_name))
    click.echo('    Branch: {}'.format(branch_name))

    config = _initialize_config(config_file_name)

    if not sync_path:
        sync_path = config['COPY_PATH']

    repo_dir = util.construct_path(sync_path, locals(), repo_name)
    repo_url = "https://%s/%s/%s" % (domain, account, repo_name)

    if not os.path.exists(repo_dir):
        _initialize_repo(
            repo_url,
            repo_dir,
            branch_name,
            config
        )

    repo = git.Repo(repo_dir)
    _make_commit_if_dirty(repo, repo_dir)
    _pull_and_resolve_conflicts(repo, branch_name, progress=None)

    return 'Pulled from repo: ' + repo_name


def _initialize_repo(repo_url, repo_dir, branch_name, config, progress=None):
    """
    Clones repository.
    """
    click.echo('Repo {} doesn\'t exist. Cloning...'.format(repo_dir))

    # Clone repo
    repo = git.Repo.clone_from(
        repo_url,
        repo_dir,
        progress,
        branch=branch_name,
    )

    click.echo('Repo {} initialized'.format(repo_url))


def _initialize_config(config_file_name):
    if not os.path.isfile(config_file_name):
        try:
            os.makedirs(os.path.dirname(config_file_name))
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

        with open(config_file_name, 'w') as config_file:
            config_file.write(DEFAULT_CONFIG_CONTENTS)

    with open(config_file_name) as config_file:
        return json.load(config_file)


def _make_commit_if_dirty(repo, repo_dir):
    """
    Makes a commit with message 'WIP' if there are changes.
    """
    if repo.is_dirty():
        git_cli = repo.git
        git_cli.add('-A')
        git_cli.commit('-m', 'WIP')
        click.echo('Made WIP commit')


def _pull_and_resolve_conflicts(repo, branch, progress=None):
    """
    Git pulls, resolving conflicts with -Xours
    """
    click.echo('Starting pull from {}'.format(repo.remotes['origin']))

    git_cli = repo.git

    # Fetch then merge, resolving conflicts by keeping original content
    repo.remote(name='origin').fetch(progress=progress)
    git_cli.merge('-Xours', 'origin/' + branch)

    click.echo('Pulled from {}'.format(repo.remotes['origin']))
