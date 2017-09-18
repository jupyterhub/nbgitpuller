# nbgitpuller

One-way synchronization of a remote git repository to a local git repository,
with automatic conflict resolution.

# Installation

There is no package on PyPI available right now. You can install directly from master:

    pip install git+https://github.com/data-8/gitautosync

You can then enable the serverextension

    jupyter serverextension enable --py nbgitpuller --sys-prefix

# What is it?

nbgitpuller allows you to construct URL that points to a remote git repository.
When it is clicked, nbgitpuller will pull for the contents of this repository
into the user's current folder within Jupyter, while rendering a nice status page.
This is especially useful when running on a JupyterHub, since it allows easy distribution
of materials to users without requiring them to understand git.

# Merging behavior

When a link is clicked, we try to make opinionated intelligent guesses on how to
do a merge automatically, without making the user have to do a conflict resolution.
nbgitpuller is designed to be used by folks who do not know that git is being used
underneath, and are only pulling content one way from a source and modifying it -
not pushing it back.
So we have made the following opinionated decisions.


1. If content has changed in both places, prefer local changes over remote changes.
2. If a file was deleted locally but present in the remote, remote file is restored
   to local repository. This allows users to get a 'fresh copy' of a file by
   just deleting the file locally & clicking the link again.
3. If a file exists locally but is untracked by git (maybe someone uploaded it manually),
   then rename the file, and pull in remote copy.

# Constructing the nbgitpuller URL

You can construct a working nbgitpuller URL like this:

```
myjupyterhub.org/hub/user-redirect/git-pull?repo=<your-repo-url>&branch=<your-branch-name>&subPath=<subPath>
```

- **repo** is the URL of the git repository you want to clone. This paramter is required.
- **branch** is the branch name to use when cloning from the repository.
  This parameter is optional and defaults to `master`.
- **subPath** is the path of the directory / notebook inside the repo to launch after cloning.
  This parameter is optional, and defaults to opening the base directory of the linked Git repository.
