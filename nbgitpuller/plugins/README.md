# [nbgitpuller download plugins](https://github.com/jupyterhub/nbgitpuller)

`nbgitpuller` download plugins enable users to download compressed
archives(zip or tar-compatible) into jupyter hubs from any publicly accessible URL
including from services such as Google Drive and Dropbox. Each plugin in this directory
includes a README file describing the format of the URL expected from each provider.

You can install some or all of the plugins into your environment. They are automatically
discovered by the system; we used pluggy(https://pluggy.readthedocs.io/en/stable/) to handle
the loading and implementation of these plugins.

If you would like to add a provider, you can mimic the plug-in format in one of the provided
examples, install it into your jupyterhub environment and it will be automatically discovered
by nbgitpuller.


## Installation

```shell
python3 -m pip install nbgitpuller-dropbox
python3 -m pip install nbgitpuller-googledrive
python3 -m pip install nbgitpuller-standard
```
