import os
import re
import json
import click
import git
import errno
from . import util


DEFAULT_CONFIG_CONTENTS = '\
{\n\
    "COPY_PATH": "",\n\
    "ALLOWED_WEB_DOMAINS": "github.com",\n\
    "GITHUB_DOMAIN": "github.com",\n\
    "ALLOWED_GITHUB_ACCOUNTS": "data-8",\n\
    "GITHUB_API_TOKEN": "",\n\
    "MOCK_AUTH": true,\n\
    "AUTO_PULL_LIST_FILE_NAME": ".autopull_list"\n\
}'

def pull_from_remote(username, repo_name, branch_name, paths, config_file_name, sync_path, account, domain):
    """
    Initializes git repo if needed, then pulls new content from remote repo using
    sparse checkout.

    Additional options include:

    domain (by default domain=github.com)
    account (only used when domain=github.com, by default account=data-8)

    The result is equivalent to:

    if domain == github.com:
        git [clone] https://<API_TOKEN>@<domain>/<account>/<repo>.git
    else:
        git [clone] https://<API_TOKEN>@<domain>/<repo>.git

    The user will be redirected to the lab01.ipynb notebook in the gh_pages branch
    (and open it).

    This pull preserves the original content in case of a merge conflict by
    making a WIP commit then pulling with -Xours.

    It resets deleted files back to their original state before a pull to allow
    getting back the original file more easily.

    Reference:
    http://jasonkarns.com/blog/subdirectory-checkouts-with-git-sparse-checkout/

    Required kwargs:
        domain (str): Domain to pull from
        account (str): (Github) account to use
        username (str): The username of the JupyterHub user
        repo_name (str): The repo under the dsten org to pull from, eg.
            textbook or health-connector.
        branch_name (str): Name of the branch in the repo.
        paths (list of str): The folders and file names to pull.
        config (Config): The config for this environment.

    Returns:
        A return string message
    """

    assert repo_name and branch_name and paths and config_file_name

    config = _initialize_config(config_file_name)

    if not sync_path:
        sync_path = config['COPY_PATH']

    click.echo('Starting pull.')
    click.echo('    User: {}'.format(username))
    click.echo('    Domain: {}'.format(domain))
    click.echo('    Account: {}'.format(account))
    click.echo('    Repo: {}'.format(repo_name))
    click.echo('    Branch: {}'.format(branch_name))
    click.echo('    Paths: {}'.format(paths))

    # Retrieve file form the git repository
    repo_dir = util.construct_path(sync_path, locals(), repo_name)
    repo_url = ''
    # Generate repo url
    if domain not in config['ALLOWED_WEB_DOMAINS']:
        click.echo("Allowed domains: " + str(config['ALLOWED_WEB_DOMAINS']))
        click.echo("Specified domain " + domain + " is not allowed.", err=True)
        return "Specified domain " + domain + " is not allowed."
    if domain == config['GITHUB_DOMAIN']:
        if account not in config['ALLOWED_GITHUB_ACCOUNTS']:
            click.echo("Specified github account " + account + " is not allowed.", err=True)
            return "Specified github account " + account + " is not allowed."
        repo_url += _generate_repo_url("https", domain,
                                       account, repo_name, config['GITHUB_API_TOKEN'])
    else:
        repo_url += _generate_repo_url("https",
                                       domain, '', repo_name)

    try:
        _update_auto_pull_file(config, repo_name, domain, account, branch_name)

        if not os.path.exists(repo_dir):
            _initialize_repo(
                repo_url,
                repo_dir,
                branch_name,
                config
            )

        repo = git.Repo(repo_dir)

        for path in paths:
            _raise_error_if_git_file_not_exists(repo, branch_name, path)

        _add_sparse_checkout_paths(repo_dir, paths)

        _reset_deleted_files(repo, branch_name)
        _make_commit_if_dirty(repo, repo_dir)

        _pull_and_resolve_conflicts(repo, branch_name, progress=None)

        return 'Pulled from repo: ' + repo_name

    except git.exc.GitCommandError as git_err:
        click.echo(git_err.stderr, err=True)
        return git_err.stderr

    finally:
        # Always set ownership to username in case of a git failure
        # In development, don't run the chown since the sample user doesn't
        # exist on the system.
        if config['MOCK_AUTH']:
            click.echo("We're in development so we won't chown the dir.")
        else:
            util.chown_dir(repo_dir, username)


def _initialize_repo(repo_url, repo_dir, branch_name, config, progress=None):
    """
    Clones repository and configures it to use sparse checkout.
    Extraneous folders will get removed later using git read-tree
    """
    click.echo('Repo {} doesn\'t exist. Cloning...'.format(repo_url))
    # Clone repo
    repo = git.Repo.clone_from(
        repo_url,
        repo_dir,
        progress,
        branch=branch_name,
    )

    # Use sparse checkout

    config = repo.config_writer()
    config.set_value('core', 'sparsecheckout', True)
    config.release()

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


DELETED_FILE_REGEX = re.compile(
    r"deleted:\s+"  # Look for deleted: + any amount of whitespace...
    r"([^\n\r]+)"        # and match the filename afterward.
)

ADDED_FILE_REGEX = re.compile(
    r"new file:\s+"  # Look for deleted: + any amount of whitespace...
    r"([^\n\r]+)"    # and match the filename afterward.
)


def _update_auto_pull_file(config, repo_name, domain, account, branch_name):
    file_name = config["AUTO_PULL_LIST_FILE_NAME"]

    existing_pulls = []
    try:
        auto_pull_file = open(file_name, 'r')
        with auto_pull_file as auto_file:
            existing_pulls = [line.strip() for line in auto_file.readlines()]
    except FileNotFoundError:
        open(file_name, 'w')

    click.echo(
        'Existing pulls in {}: {}'.format(file_name, existing_pulls))

    new_pull = "{},{},{},{}".format(repo_name, domain, account, branch_name)

    if new_pull not in existing_pulls:
        with open(file_name, 'a') as auto_file:
            auto_file.write('{}\n'.format(new_pull))


def _reset_deleted_files(repo, branch_name):
    """
    Runs the equivalent of git checkout -- <file> for each file that was
    deleted. This allows us to delete a file, hit an interact link, then get a
    clean version of the file again.
    """
    git_cli = repo.git
    deleted_files = DELETED_FILE_REGEX.findall(git_cli.status())

    if deleted_files:
        cleaned_filenames = []

        for filename in deleted_files:
            try:
                _raise_error_if_git_file_not_exists(repo, branch_name, filename)
                cleaned_filenames.append(_clean_path(filename))
            except git.exc.GitCommandError as git_err:
                pass

        git_cli.checkout('--', *cleaned_filenames)
        click.echo('Resetted these files: {}'.format(deleted_files))


def _clean_path(path):
    """
    Clean filename so that it is command line friendly.

    Currently just escapes spaces.
    """
    return path.replace(' ', '\ ')


def _raise_error_if_git_file_not_exists(repo, branch_name, filename):
    """
    Checks to see if the file or directory actually exists in the remote repo
    using: git cat-file -e origin/<branch_name>:<filename>
    """
    git_cli = repo.git

    # fetch origin first so that cat-file can see if the file exists
    try:
        git_cli.fetch()
    except git.exc.GitCommandError as git_err:
        pass

    result = git_cli.cat_file('-e', 'origin/' + branch_name + ':' + filename)


def _add_sparse_checkout_paths(repo_dir, paths):
    """
    Runs the equivalent of

    echo /path >> .git/info/sparse-checkout

    for each path in paths but also avoids duplicates.

    Always makes sure .gitignore is checked out
    """
    sparse_checkout_path = os.path.join(repo_dir,
                                        '.git', 'info', 'sparse-checkout')

    existing_paths = []
    try:
        sparse_checkout_file = open(sparse_checkout_path, 'r')
        with sparse_checkout_file as info_file:
            existing_paths = [line.strip().strip('/')
                              for line in info_file.readlines()]
    except FileNotFoundError:
        # If .git/info/sparse-checkout does not exist, create the file
        open(sparse_checkout_path, 'w')

    click.echo(
        'Existing paths in sparse-checkout: {}'.format(existing_paths))

    paths_with_gitignore = ['.gitignore'] + paths
    to_write = [path for path in paths_with_gitignore
                if path not in existing_paths]

    with open(sparse_checkout_path, 'a') as info_file:
        for path in to_write:
            info_file.write('/{}\n'.format(_clean_path(path)))

    click.echo('{} written to sparse-checkout'.format(to_write))


def _make_commit_if_dirty(repo, repo_dir):
    """
    Makes a commit with message 'WIP' if there are changes.
    """
    if repo.is_dirty():
        git_cli = repo.git
        git_cli.add('-A')

        added_files = ADDED_FILE_REGEX.findall(git_cli.status())

        if added_files:
            sparse_checkout_path = os.path.join(repo_dir,
                                        '.git', 'info', 'sparse-checkout')

            try:
                open(sparse_checkout_path, 'r')
            except FileNotFoundError:
                open(sparse_checkout_path, 'w')

            with open(sparse_checkout_path, 'a') as info_file:
                for path in added_files:
                    info_file.write('/{}\n'.format(_clean_path(path)))

            click.echo('Added these files: {}'.format(added_files))

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

    # Ensure only files/folders in sparse-checkout are left
    git_cli.read_tree('-mu', 'HEAD')

    click.echo('Pulled from {}'.format(repo.remotes['origin']))
