import argparse
from .pull_from_remote import pull_from_remote


def main():
    """
    Synchronizes a github repository with a local repository.
    Automatically deals with conflicts and produces useful output to stdout.
    """
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--git-url', default='https://github.com/data-8/summer.git', help='Url of the repo to sync')
    parser.add_argument('--branch-name', default='gh-pages', help='Branch of repo to sync')
    parser.add_argument('--repo-dir', default='summer', help='Path to sync to')
    args = vars(parser.parse_args())
    pull_from_remote(**args)
