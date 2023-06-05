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

## Development

Setup development environment

```
# clone git repo
git clone git@github.com:hydroshare/nbfetch.git && cd nbfetch

# create and activate python environment
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip

# install nbfetch in edit mode
pip install -e .

# enable jupyter_server extension
jupyter server extension enable --py nbfetch

# start jupyter lab
jupyter lab
```

`nbfetch` requires HydroShare user authentication (username, password) or authorization (OAuth2) to
function. HydroShare user authentication can be provided in two ways, by file or via environment
variables (see below). At this time, we do not have guidance for supplying using authorization
(OAuth2) in a development environment.

### Authentication Locations

HydroShare user authentication can be provided using either files or environment variables.
`nbfetch` will look for authentication information in the following locations:

Note: files take precedence over environment variables

file locations:

- `~/.hs_user`
- `~/.hs_pass`

environment variables:

- `HS_USER`
- `HS_PASS`
