.. _topic/url-options:

=============================
Options in an nbgitpuller URL
=============================

.. note::

   If you just want to generate an nbgitpuller link, we highly
   recommend just using the :doc:`link generator <../link>`

Most aspects of the nbgitpuller student experience can be configured
with various options in the nbgitpuller URL. This page documents
the various options available, and their behavior.

``repo``
========

The path to the git repository to be pulled from. This will accept
any parameter that can be passed to a ``git clone`` command.

``branch``
==========

Branch in the git repo to pull from. Defaults to ``master``.

``urlpath``
===========

The URL to redirect the user to after synchronization has been complete. This
URL is primarily used to open a specific file or directory in a specific
application. This URL is interpreted relative to the base of the notebook
server. The URL to be specified depends on the application you want
the file to be opened in.

.. warning::

   ``<full-path-to-file>`` is relative to the directory the notebook
   server was launched in - so the directory you see if you login to
   JupyterHub regularly. This means you **must** include the name of
   the local repository directory too, otherwise nbgitpuller can not
   find the file.

   For example, if the repository you are cloning is
   ``https://github.com/my-user/my-repository``, and the file you want
   your students to see is ``index.ipynb``, then ``<full-path-to-file>``
   should be ``my-repository/index.ipynb``, **not** ``index.ipynb``.

   The :doc:`link generator <../link>`
   takes care of all of this for you, so it is recommended to use that.


Classic Jupyter Notebook
------------------------

To open a notebook, file or directory in the classic Jupyter Notebook
interface, your pattern should be: ``/tree/<full-path-to-file>``.

JupyterLab
----------

To open a notebook, file or directory in the classic Jupyter Notebook
interface, your pattern should be:
``/lab/tree/<full-path-to-file>%3Fautodecode``.

The ``%3Fautodecode`` at the end makes sure you never get `a message
<https://github.com/jupyterlab/jupyterlab/pull/5950>`_ about needing to
explicitly name a JupyterLab workspace.

Shiny
-----

To open a directory containing `shiny <https://shiny.rstudio.com/>`_ files,
your pattern should be ``/shiny/<full-path-to-directory>/``. The trailing
slash is important.

RStudio
-------

If you have RStudio installed and set up for use with your JupyterHub,
you can pass ``/rstudio`` to ``urlpath`` to open RStudio after the
repo has been pulled. You can not have RStudio open a specific file
or directory, unfortunately.

``depth``
=========

How deep to clone the git repo on initial pull. By default, the
entire history of the git repository is pulled. This might be
slow if your git repository is large. You can set this to 1 to
pull only the latest commit on initial pull.

Only explicitly set this if you are actively having performance
problems.


``targetPath``
==============

Where to place the repository when it is cloned.
By default, Git repositories are cloned into the default working directory.
You can specify a different parent directory for the clone by setting the environment variable ``NBGITPULLER_PARENTPATH``, this should be relative to the working directory.
If you require full control over the destination directory, or want to set the directory at runtime in the nbgitpuller link use this parameter.


Deprecated parameters
=====================

The following parameters are currently deprecated, and will be removed in
a future version: ``subpath``, ``app``.
