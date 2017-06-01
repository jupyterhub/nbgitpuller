import argparse
from .pull_from_remote import pull_from_remote


def main():
    """
    Synchronizes a github repository with a local repository.
    Automatically deals with conflicts and produces useful output to stdout.
    """
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--repo-name', default='summer', help='Name of the repo to sync')
    parser.add_argument('--account', default='data-8', help='Account of the repo to sync')
    parser.add_argument('--branch-name', default='gh-pages', help='Branch of repo to sync')
    parser.add_argument('--sync-path', default='', help='Path to sync to')
    parser.add_argument('--domain', default='github.com', help='git domain')
    args = vars(parser.parse_args())
    pull_from_remote(**args)
