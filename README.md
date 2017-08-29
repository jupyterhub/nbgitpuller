# gitautosync

Synchronizes a github repository with a local repository. Automatically deals with conflicts and produces useful output to stdout.


# Installation

Before installing, make sure you have a **Python 3** installation with
the Jupyter environment installed.

To install gitautosync, first install the package with `pip`. You should install
the ``master`` branch of ``gitautosync``:

    pip install git+https://github.com/data-8/gitautosync

Next, enable the server extension with the following command:

    jupyter serverextension enable --py nbgitautosync --sys-prefix


# Usage

To use gitautosync, open the notebook. Depending whether you are working
locally or via a JupyterHub, you'll use different syntax.

If you're working off of a JupyterHub, use this syntax:

    myjupyterhub.com/hub/user-redirect/git-sync?repo=<URL-to-my-repo>

If you're working locally, use this syntax:

    localhost:8888/git-sync?repo=<URL-to-my-repo>

The repository will be cloned and placed in your root folder. If this
repository already exists in your root folder, then files will be updated
with any changes that exist in the repository from which we are pulling.
If there are any merge conflicts, the user version will be kept, so your
work won't be overwritten.
