# nbgitpuller

One-way synchronization of a remote git repository to a local git repository,
with automatic conflict resolution.

# Installation

There is no package on PyPI available right now. You can install directly from master:

    pip install git+https://github.com/data-8/gitautosync

You can then enable the serverextension

    jupyter serverextension enable --py nbgitpuller --sys-prefix

# How it works

nbgitpuller works by allowing you to construct a special URL, that when clicked
will do the pulling for the user while rendering a nice status page. This is
especially useful when running on a JupyterHub, since it allows easy distribution
of materials to users without them having to understand git.

# Constructing the nbgitpuller URL

You can construct a working nbgitpuller URL like this:

```
myjupyterhub.org/hub/user-redirect/git-sync?repo=<your-repo-url>&branch=<your-branch-name>&subPath=<subPath>
```

- **repo** is the URL of the git repository you want to clone. This paramter is required.
- **branch** is the branch name to use when cloning from the repository.
  This parameter is optional and defaults to `master`.
- **subPath** is the path of the directory / notebook inside the repo to launch after cloning.
  This parameter is optional and defaults to just opening the directory containing contents of
  your repository.
