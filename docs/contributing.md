# Contributing

## Setup

nbgitpuller is a jupyter extension that works with both the
[classic Notebook Server](https://jupyter-notebook.readthedocs.io/en/stable/extending/handlers.html),
and the newer [Jupyter Server](https://jupyter-server.readthedocs.io/en/latest/operators/configuring-extensions.html).
Hence, nbgitpuller can be developed locally without needing a JupyterHub.

1. Fork the nbgitpuller repository and `git clone` it to your local computer.

2. Inside the nbgitpuller clone on your local machine, setup a virtual
   environment to do development in

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install development time dependencies in this virtual environment

   ```bash
   pip install -r dev-requirements.txt
   ```

4. Install nbgitpuller with its dependencies in this virtual environment

   ```bash
   pip install -e .
   ```

5. Install the NodeJS dependencies from package.json.

   ```bash
   npm install
   ```

6. Create the JS and CSS bundles.

   ```bash
   npm run webpack
   ```

7. Enable the nbgitpuller extension:
   * as a jupyter serverextension (classic Notebook Server extension)

      ```bash
      jupyter serverextension enable --sys-prefix nbgitpuller
      ```
   * as a jupyter server extension
      ```bash
      jupyter server extension enable --sys-prefix nbgitpuller
      ```

8. Start the notebook server:

   * You can either start the classical Notebook server.
   This will open the classic notebook in your web
   browser, and automatically authenticate you as a side effect.

      ```bash
      jupyter notebook
      ```

   * Or you can start the new Jupyter Server.
      ```bash
      jupyter server
      ```
      This won't open any notebook interface, unless you don't enable one
      ([`nbclassic`](https://github.com/jupyterlab/nbclassic) or [`jupyterlab`](https://github.com/jupyterlab/jupyterlab))
      as a jupyter server extension.
      ```bash
      jupyter server extension enable --sys-prefix nbclassic
      ```
      or
      ```bash
      jupyter server extension enable --sys-prefix jupyterlab
      ```

9. You can now test nbgitpuller locally, by hitting the `/git-pull` url with any
   of the [URL query parameters](topic/url-options.rst). For example, to pull the
   [data-8/textbook](https://github.com/data-8/textbook) repository's `gh-pages`
   branch, you can use the following URL:

   ```
   http://localhost:8888/git-pull?repo=https://github.com/data-8/textbook&branch=gh-pages
   ```

10. If you make changes to nbgitpuller's python code, you need to restart the `jupyter notebook`
   process (started in step 5) to see your changes take effect. This is not needed if
   you are only working on the javascript or css.

## Running the flake8 linter

[flake8](https://flake8.pycqa.org/en/latest/) is used to validate python coding style. The
flake8 config is in `.flake8`, and is not super strict. You should be able to run
`flake8` in the root directory of the repository to get a list of issues to be fixed.

## Running tests

[pytest](https://docs.pytest.org/) is used to run unit and integration tests,
under the `tests/` directory. If you add new functionality, you should also add
tests to cover it.  You can run the tests locally with `py.test tests/`

## Building documentation

[sphinx](https://www.sphinx-doc.org/) is used to write and maintain documentation, under
the `docs/` directory. If you add any new functionality, you should write documentaiton
for it as well. A mix of [reStructuredText](https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html)
and [MyST Markdown](https://myst-parser.readthedocs.io) is used to write our documentation,
although we would like to migrate purely to MyST markdown in the future.

1. Install the packages needed to build the documentation

   ```bash
   pip install -r docs/doc-requirements.txt
   ```

2. Build the documentation by using `make` inside the `docs` folder. This will
   internally call `sphinx`

   ```bash
   cd docs
   make html
   ```

3. Preview the documentation by opening `_build/html/index.html` file in
   your browser. From inside the `docs` folder, you can run either
   `open _build/html/index.html` (on MacOS) or `xdg-open _build/html/index.html`
   to quickly open the file in the browser.

4. You can run `make html` again after making further changes to see their
   effects.
