import os
import subprocess


def pull_from_remote(repo_name, branch_name, sync_path, account, domain):
    """
    Pull selected repo from a remote git repository,
    while preserving user changes
    """
    assert repo_name and branch_name and account and domain

    print('Starting pull.')
    print('    Domain: {}'.format(domain))
    print('    Repo: {}'.format(repo_name))
    print('    Branch: {}'.format(branch_name))

    repo_dir = os.path.join(sync_path, repo_name)
    repo_url = "https://%s/%s/%s.git" % (domain, account, repo_name)

    if not os.path.exists(repo_dir):
        return _initialize_repo(repo_url, repo_dir, branch_name)

    _make_commit_if_dirty(repo_dir, branch_name)
    _pull_and_resolve_conflicts(repo_url, repo_dir, branch_name)

    print('Pulled from repo: {}'.format(repo_name))


def _initialize_repo(repo_url, repo_name, branch_name):
    """
    Clones repository.
    """
    print('Repo {} doesn\'t exist. Cloning...'.format(repo_name))

    # Clone repo
    subprocess.run(['git', 'clone', repo_url])
    subprocess.run(['git', 'checkout', branch_name])

    print('Repo {} initialized'.format(repo_url))


def _make_commit_if_dirty(repo_dir, branch_name):
    """
    Makes a commit with message 'WIP' if there are changes.
    """
    cwd = _get_sub_cwd(repo_dir)
    if _repo_is_dirty(repo_dir):
        subprocess.Popen(['git', 'checkout', branch_name], cwd=cwd)
        subprocess.Popen(['git', 'add', '-A'], cwd=cwd)
        subprocess.Popen(['git', 'commit', '-m', 'WIP'], cwd=cwd)
        print('Made WIP commit')


def _pull_and_resolve_conflicts(repo_url, repo_dir, branch_name):
    """
    Git pulls, resolving conflicts with -Xours
    """
    print('Starting pull from {}'.format(repo_url))

    # Fetch then merge, resolving conflicts by keeping original content
    cwd = _get_sub_cwd(repo_dir)
    subprocess.run(['git', 'checkout', branch_name], cwd=cwd)
    subprocess.Popen(['git', 'fetch'], cwd=cwd)
    subprocess.Popen(['git', 'merge', '-Xours', 'origin/{}'.format(branch_name)], cwd=cwd)

    print('Pulled from {}'.format(repo_url))


def _get_sub_cwd(repo_dir):
    return '{}/{}'.format(os.getcwd(), repo_dir)


def _repo_is_dirty(repo_dir):
    p = subprocess.Popen(['git', 'diff-index', '--name-only', 'HEAD', '--'], cwd=_get_sub_cwd(repo_dir))
    out, err = p.communicate()
    return out
