import click
from .pull_from_remote import pull_from_remote

@click.command()
@click.option('--repo-name', prompt='Repo name', default='world', help='Name of the repo to sync')
@click.option('--branch-name', prompt='Branch name', default='world', help='Branch of repo to sync')
@click.option('--paths', prompt='Paths', default='world', help='Paths to sync')
@click.option('--config', prompt='Config file name', default='world', help='Config file name')
@click.option('--sync-path', default='world', help='Path to sync to')
@click.option('--account', default='world', help='git account')
@click.option('--domain', default='world', help='git domain')
def main(repo_name, branch_name, paths, config, sync_path, account, domain):
    """
    Synchronizes a github repository with a local repository.
    Automatically deals with conflicts and produces useful output to stdout.
    """
    click.echo('{0}, {1}.'.format(repo_name, branch_name))
