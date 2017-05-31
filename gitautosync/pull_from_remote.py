import os
import json
import click
import git
import errno


def pull_from_remote(repo_name, branch_name, sync_path, account, domain):
    """
    Pull selected repo from a remote git repository,
    while preserving user changes
    """
    assert repo_name and branch_name and account and domain

    click.echo('Starting pull.')
    click.echo('    Domain: {}'.format(domain))
    click.echo('    Repo: {}'.format(repo_name))
    click.echo('    Branch: {}'.format(branch_name))

    repo_dir = os.path.join(sync_path, repo_name)
    repo_url = "https://%s/%s/%s" % (domain, account, repo_name)
    repo = _get_repo(repo_url, repo_dir, branch_name)

    _make_commit_if_dirty(repo)
    _pull_and_resolve_conflicts(repo)

    return 'Pulled from repo: ' + repo_name


def _get_repo(repo_url, repo_dir, branch_name):
    """
    Returns repo object of repo to update
    """
    if not os.path.exists(repo_dir):
        return _initialize_repo(repo_url, repo_dir, branch_name)
    else:
        return git.Repo(repo_dir)


def _initialize_repo(repo_url, repo_dir, branch_name):
    """
    Clones repository.
    """
    click.echo('Repo {} doesn\'t exist. Cloning...'.format(repo_dir))

    # Clone repo
    repo = git.Repo.clone_from(
        repo_url,
        repo_dir,
        branch=branch_name,
    )

    click.echo('Repo {} initialized'.format(repo_url))

    return repo


def _make_commit_if_dirty(repo):
    """
    Makes a commit with message 'WIP' if there are changes.
    """
    commit = None
    if repo.is_dirty():
        git_cli = repo.git
        git_cli.add('-A')
        commit = git_cli.commit('-m', 'WIP')
        click.echo('Made WIP commit')

    return commit


def _pull_and_resolve_conflicts(repo):
    """
    Git pulls, resolving conflicts with -Xours
    """
    click.echo('Starting pull from {}'.format(repo.remotes['origin']))

    # Fetch then merge, resolving conflicts by keeping original content
    repo.remote(name='origin').fetch()
    git_cli = repo.git
    merge = git_cli.merge('-Xours', 'origin/' + repo.active_branch.name)

    click.echo('Pulled from {}'.format(repo.remotes['origin']))
    return merge
