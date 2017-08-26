# gitautosync

Synchronizes a github repository with a local repository. Automatically deals with conflicts and produces useful output to stdout.


# Installation

Before installing, make sure you have a **Python 3** installation with
the Jupyter environment installed.

To install gitautosync, first install the package with `pip`:

    pip install gitautosync

Next, enable the server extension with the following command:

    jupyter serverextension enable --py nbgitautosync --sys-prefix


# Usage

To use gitautosync, open the notebook. Replace `tree` (and everything)
after it with the following syntax:

    myjupyterhub.com/git-sync?repo=<URL-to-my-repo>

The repository will be cloned and placed in your root folder. If this
repository already exists in your root folder, then files will be updated
with any changes that exist in the repository from which we are pulling.
If there are any merge conflicts, the user version will be kept, so your
work won't be overwritten.
