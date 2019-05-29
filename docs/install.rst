.. _install:

============
Installation
============

You can install ``nbgitpuller`` from PyPI with ``pip`` in the same
environment where your jupyter notebook package is installed.

.. code:: bash

   pip install nbgitpuller

Troubleshooting
===============

nbgitpuller link shows `404 Not Found` 
-------------------------------------

If you are on an old version of Jupyter Notebook, you might get a `404 Not Found`
error when trying to access an nbgitpuller link. You might need to manually enable
the server extension that handles nbgitpuller.

.. code:: bash

   jupyter serverextension enable nbgitpuller --sys-prefix
