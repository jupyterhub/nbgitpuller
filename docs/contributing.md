# Contributing

## Setup

nbgitpuller is a [jupyter
serverextension](https://jupyter-notebook.readthedocs.io/en/stable/extending/handlers.html),
and hence can be developed locally without needing a JupyterHub.

1. Fork the nbgitpuller repository and `git clone` it to your local computer.

2. Inside the nbgitpuller clone on your local machine, setup a virtual
   environment to do development in

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install nbgitpuller with its dependencies in this virtual environment

   ```bash
   pip install -e .
   ```

4. Enable the nbgitpuller jupyter serverextension

   ```bash
   jupyter serverextension enable --sys-prefix nbgitpuller
   ```

5. Start the notebook server. This will open the classic notebook in your web
   browser, and automatically authenticate you as a side effect.

   ```bash
   jupyter notebook
   ```

6. You can now test nbgitpuller locally, by hitting the `/git-pull` url with any
   of the [URL query parameters](topic/url-options.rst). For example, to pull the
   [data-8/textbook](https://github.com/data-8/textbook) repository's `gh-pages`
   branch, you can use the following URL:

   ```
   http://localhost:8888/git-sync?repo=https://github.com/data-8/textbook&branch=gh-pages
   ```
