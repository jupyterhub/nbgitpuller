# NBGitpuller

Create links for one-way synchronization of a remote git repository to a local git repository,
with automatic conflict resolution. Meant for use with a Jupyter server.

![nbgitpuller demo](_static/nbpuller.gif)

## Contents

See below for some helpful links on how to use `nbgitpuller`.

* [Using nbgitpuller](using.md)
* [Generate your own nbgitpuller links here](link.rst)
* [YouTube video instructions for teachers.](https://youtu.be/o7U0ZuICVFg)

## Installation

You can install nbgitpuller from PyPI.

    pip install nbgitpuller

You can then enable the serverextension

    jupyter serverextension enable --py nbgitpuller --sys-prefix

## What is it?

nbgitpuller allows you to construct a URL that points to a remote git repository.
When it is clicked, nbgitpuller will pull the contents of this repository
into the user's current folder within Jupyter, while rendering a nice status page.
This is especially useful when running on a JupyterHub, since it allows easy distribution
of materials to users without requiring them to understand git.

## Merging behavior

When a link is clicked, we try to make opinionated intelligent guesses on how to
do a merge automatically, without making the user do a conflict resolution.
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