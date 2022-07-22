# nbfetch

Fork of nbgitpuller allowing access to Hydroshare resources.

-------------------

One-way synchronization of a remote git repository to a local git repository,
with automatic conflict resolution.

Pull Hydroshare resources to a local directory.

## Installation

```shell
# install
pip install -U --no-cache-dir --upgrade-strategy only-if-needed git+https://github.com/hydroshare/nbfetch

# enable jupyter_server extension
jupyter server extension enable --py nbfetch
```

## Usage

See https://github.com/jupyterhub/nbgitpuller.

Additional Hydroshare functionality allows useds to download a resource and optionally start a notebook in that resource.

Example on a local Jupyter installation.

  http://localhost:8888/hs-pull?id=8caa62c46c424a818899ebeca6f30a83&start=spiro3D.ipynb

On JupyterHub,

  https://jupyterhub-dev.uwrl.usu.edu/hub/user-redirect/hs-pull?id=8caa62c46c424a818899ebeca6f30a83&start=spiro3D.ipynb