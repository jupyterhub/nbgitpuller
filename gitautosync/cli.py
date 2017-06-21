import argparse
from .pull_from_remote import pull_from_remote


def main():
    """
    Synchronizes a github repository with a local repository.
    Automatically deals with conflicts and produces useful output to stdout.
    """
    parser = argparse.ArgumentParser(description='Synchronizes a github repository with a local repository.')
    parser.add_argument('--git-url', help='Url of the repo to sync', required=True)
    parser.add_argument('--branch-name', default='master', help='Branch of repo to sync')
    parser.add_argument('--repo-dir', default='./', help='Path to sync to')
    args = parser.parse_args()
    pull_from_remote(args.git_url, args.branch_name, args.repo_dir)
