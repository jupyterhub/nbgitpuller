import os
import json
import click
import git
import errno


DEFAULT_CONFIG_CONTENTS = '\
{\n\
    "COPY_PATH": "",\n\
    "GITHUB_DOMAIN": "github.com",\n\
    "ALLOWED_GITHUB_ACCOUNTS": "data-8",\n\
    "MOCK_AUTH": true\n\
 }'


def pull_from_remote(repo_name, branch_name, config_file_name, sync_path, account, domain):
    """
    Pull selected repo from a remote git repository,
    while preserving user changes
    """
    assert repo_name and branch_name and config_file_name

    click.echo('Starting pull.')
    click.echo('    Domain: {}'.format(domain))
    click.echo('    Repo: {}'.format(repo_name))
    click.echo('    Branch: {}'.format(branch_name))

    config = _read_config_file(config_file_name)
    sync_path = sync_path if sync_path else config['COPY_PATH']
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


def _initialize_config(config_file_name):
    """
    Initializes a json config file with default values if doesn't exist
    """
    try:
        os.makedirs(os.path.dirname(config_file_name))
        with open(config_file_name, 'w') as config_file:
            config_file.write(DEFAULT_CONFIG_CONTENTS)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


def _read_config_file(config_file_name):
    """
    Return contents of json config file as dict
    """
    if not os.path.isfile(config_file_name):
        _initialize_config(config_file_name)

    with open(config_file_name) as config_file:
        return json.load(config_file)


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
