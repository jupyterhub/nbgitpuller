# [nbgitpuller](https://github.com/jupyterhub/nbgitpuller)


[![GitHub Workflow Status - Test](https://img.shields.io/github/workflow/status/jupyterhub/nbgitpuller/Tests?logo=github&label=tests)](https://github.com/jupyterhub/nbgitpuller/actions)
[![CircleCI build status](https://img.shields.io/circleci/build/github/jupyterhub/nbgitpuller?logo=circleci&label=docs)](https://circleci.com/gh/jupyterhub/nbgitpuller)
[![](https://img.shields.io/pypi/v/nbgitpuller.svg?logo=pypi)](https://pypi.python.org/pypi/nbgitpuller)
[![GitHub](https://img.shields.io/badge/issue_tracking-github-blue?logo=github)](https://github.com/jupyterhub/nbgitpuller/issues)
[![Discourse](https://img.shields.io/badge/help_forum-discourse-blue?logo=discourse)](https://discourse.jupyter.org/c/jupyterhub)
[![Gitter](https://img.shields.io/badge/social_chat-gitter-blue?logo=gitter)](https://gitter.im/jupyterhub/jupyterhub)

`nbgitpuller` lets you distribute content in a git repository to your students
by having them click a simple link. [Automatic
merging](https://jupyterhub.github.io/nbgitpuller/topic/automatic-merging.html)
ensures that your students are never exposed to `git` directly. It is primarily
used with a JupyterHub, but can also work on students' local computers.

See [the documentation](https://jupyterhub.github.io/nbgitpuller) for more
information.

## Installation

```shell
pip install nbgitpuller
```

## Example


This example shows how to use the  [nbgitpuller link generator](https://jupyterhub.github.io/nbgitpuller/link)
to create an nbgitpuller link, which a user then clicks.

1. The [nbgitpuller link generator GUI](https://jupyterhub.github.io/nbgitpuller/link) is used to create a
   link.

   ![](https://raw.githubusercontent.com/jupyterhub/nbgitpuller/9f380a933335f0f069b6e2f9965ed78c3abcce7a/docs/_static/nbgitpuller-link-generator.png)

2. This link is clicked, and the content is pulled into a live Jupyter session.

   ![](https://raw.githubusercontent.com/jupyterhub/nbgitpuller/9f380a933335f0f069b6e2f9965ed78c3abcce7a/docs/_static/nbgitpuller-demo.gif)
