# Generate VSCode links with nbgitpuller

nbgitpuller can launch VSCode and open a file on your JupyterHub.
It is a little different from using a Jupyter interface, so here is a rough guide.

First, ensure that [code-server](https://github.com/coder/code-server) and the [jupyter-vscode-proxy](https://github.com/betatim/vscode-binder/) (also called `vscode-binder`) are installed in your hub user environment.

Then, create a URL with the following structure:

```
https://[YOUR HUB]/hub/user-redirect/git-pull?repo=[YOUR REPO]&urlpath=vscode%2F%3Fpayload%3D%5B%5B%22openFile%22%2C%22vscode-remote%3A%2F%2F[ESCAPED PATH TO HOME DIRECTORY]%2F[ESCAPED REPO NAME]%2F[ESCAPED FILE PATH IN REPO]%22%5D%5D%0A
```

Broken up into parts, here's what that looks like:

```
https://
[YOUR HUB]
/hub/user-redirect/git-pull?repo=
[YOUR REPO]
&urlpath=vscode%2F%3Fpayload%3D%5B%5B%22openFile%22%2C%22vscode-remote%3A%2F%2F
[ESCAPED PATH TO HOME DIRECTORY]
%2F[ESCAPED REPO NAME]
%2F[ESCAPED FILE PATH IN REPO]
%22%5D%5D%0A
```

For example, the following URL will open a file called `my-script.py` in VSCode on a hub called `science.myorg.edu`:

```text
https://science.myorg.edu/hub/user-redirect/git-pull?repo=https%3A%2F%2Fgithub.com%2Fmy-username%2Fmy-repo-name&urlpath=vscode%2F%3Fpayload%3D%5B%5B%22openFile%22%2C%22vscode-remote%3A%2F%2F%2Fhome%2Fjovyan%2Fmy-repo-name%2Fmy-script.py%22%5D%5D%0A
```

and again broken down like above:

```
https://
science.myorg.edu
/hub/user-redirect/git-pull?repo=
https%3A%2F%2Fgithub.com%2Fmy-username%2Fmy-repo-name
&urlpath=vscode%2F%3Fpayload%3D%5B%5B%22openFile%22%2C%22vscode-remote%3A%2F%2F
%2Fhome%2Fjovyan
%2Fmy-repo-name
%2Fmy-script.py
%22%5D%5D%0A
```

See [this issue](https://github.com/jupyterhub/nbgitpuller/issues/397) for tracking support for VSCode in the nbgitpuller link generator.

## Caveats and gotchas

- Note the `%22%5D%5D%0A` at the end of the URL after the file path!
- This assumes your hub mounts user directories at `/home/jovyan`, which is the default for Z2JH. This may not be true for your hub!
- For example, TLJH JupyterHubs use `/home/[USERNAME]`, so this link structure won't work there.
