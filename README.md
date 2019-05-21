# nbgitpuller

Create links for one-way synchronization of a remote git repository to a local git repository,
with automatic conflict resolution. Meant for use with a Jupyter server.

* [**For more information, check out the nbgitpuller documentation**](https://jupyterhub.github.io/nbgitpuller)
* [Generate your own nbgitpuller links here](https://jupyterhub.github.io/nbgitpuller/link.html).

![nbgitpuller demo](docs/_static/nbpuller.gif)

# Installation

You can install nbgitpuller from PyPI.

    pip install nbgitpuller

You can then enable the serverextension

    jupyter serverextension enable --py nbgitpuller --sys-prefix

# What is it?

nbgitpuller allows you to construct a URL that points to a remote git repository.
When it is clicked, nbgitpuller will pull the contents of this repository
into the user's current folder within Jupyter, while rendering a nice status page.
This is especially useful when running on a JupyterHub, since it allows easy distribution
of materials to users without requiring them to understand git.

# Local development

You can easily set up to develop this locally, without requiring a JupyterHub. It requires python3.

1. Clone this repository
   ```
   git clone https://github.com/data-8/nbgitpuller
   ```

2. Change into it and create a virtual environment
   ```
   cd nbgitpuller
   python3 -m venv .
   ```

3. Install it with symlinks, so you can easily play with it.
   ```
   pip install -e .
   ```
4. Enable the jupyter notebook server extension. This provides the `git-pull` URL handlers.
   ```
   jupyter serverextension enable --sys-prefix nbgitpuller
   ```
5. Run a jupyter notebook locally!
   ```
   jupyter notebook
   ```
6. Construct a nbgitpuller URL exactly like you would for a hub, but instead of prefixing it
   with `myjupyterhub.org/hub/user-redirect`, just use `localhost:8888` or whatever the
   url of your running notebook is. For example, the following URL would pull down a repo:
   ```
   localhost:8888/git-pull?repo=https://github.com/data-8/materials-fa17
   ```
7. Make the changes you want to make, and restart the jupyter notebook for them to take effect.
