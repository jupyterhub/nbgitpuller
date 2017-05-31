import click
from .pull_from_remote import pull_from_remote


@click.command()
@click.option('--repo-name', prompt='Repo name', default='data8assets', help='Name of the repo to sync')
@click.option('--account', prompt='Account name', default='data-8', help='Account of the repo to sync')
@click.option('--branch-name', prompt='Branch name', default='gh-pages', help='Branch of repo to sync')
@click.option('--config', prompt='Config file name', default='/.gitautosync/config.json', help='Config file name')
@click.option('--domain', default='github.com', help='git domain')
def main(repo_name, branch_name, config, sync_path, account, domain):
    """
    Synchronizes a github repository with a local repository.
    Automatically deals with conflicts and produces useful output to stdout.
    """
    click.echo(pull_from_remote(repo_name, branch_name, config, sync_path, account, domain))
