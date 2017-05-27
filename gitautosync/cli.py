import os
import click
from .pull_from_remote import pull_from_remote

@click.command()
@click.option('--repo-name', prompt='Repo name', default='data8assets', help='Name of the repo to sync')
@click.option('--branch-name', prompt='Branch name', default='gh-pages', help='Branch of repo to sync')
@click.option('--paths', prompt='Paths', default=['README.md'], help='Paths to sync')
@click.option('--config', prompt='Config file name', default='/.gitautosync/config.json', help='Config file name')
@click.option('--sync-path', default='./', help='Path to sync to')
@click.option('--account', default='data-8', help='git account')
@click.option('--domain', default='github.com', help='git domain')
def main(repo_name, branch_name, paths, config, sync_path, account, domain):
    """
    Synchronizes a github repository with a local repository.
    Automatically deals with conflicts and produces useful output to stdout.
    """
    username = os.environ.get("USERNAME", "jovyan")
    click.echo(pull_from_remote(username, repo_name, branch_name, paths, config, sync_path, account, domain))
