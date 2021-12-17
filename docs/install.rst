.. _install:

============
Installation
============

nbgitpuller can work on any computer, but it is most-commonly used with a JupyterHub.
By installing nbgitpuller in the user environment for your hub, it means that
all users will be able to click nbgitpuller links to get the content.

.. admonition:: To set up a JupyterHub
   :class: tip
   
   If you do *not* have a JupyterHub, we recommend trying out `The Littlest
   JupyterHub <https://tljh.jupyter.org>`_ to set one up.
   It comes built in with nbgitpuller.

   For more information about JupyterHub, see
   `the JupyterHub Documentation <https://jupyterhub.readthedocs.io/en/stable/>`_.

You can install ``nbgitpuller`` from PyPI with ``pip``:

.. code:: bash

   pip install nbgitpuller

```{note}
If you use multiple environments in your JupyterHub, make sure you install
nbgitpuller in the environment that the jupyter notebook or
jupyter server process is running from. You can validate this by running
`jupyter serverextension list` - it should have an entry that says `nbgitpuller  enabled`.
```

Troubleshooting
===============

nbgitpuller link shows `404 Not Found` 
--------------------------------------

If you are on an old version of Jupyter Notebook, you might get a `404 Not Found`
error when trying to access an nbgitpuller link. You might need to manually enable
the server extension that handles nbgitpuller.

.. code:: bash

   jupyter serverextension enable nbgitpuller --sys-prefix
