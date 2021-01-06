===========
nbgitpuller
===========

``nbgitpuller`` lets you distribute content in a git repository to your
students by having them click a simple link. :ref:`Automatic, opinioned
conflict resolution <topic/automatic-merging>` ensures that your students are
never exposed to ``git`` directly. It is primarily used with a JupyterHub,
but can also work on students' local laptops.

.. image:: _static/nbpuller.gif

When to use nbgitpuller?
========================

You should use nbgitpuller when:

#. You are running a JupyterHub for a class & want an easy way to distribute
   materials to your students without them having to understand what git is.
#. You have a different out of band method for collecting completed
   assignments / notebooks from students, since they can not just 'push it
   back' via git.

You should **not** use nbgitpuller when:

#. You are an instructor using a JupyterHub / running notebooks locally to
   create materials and push them to a git repository. You should just use
   git directly, since the assumptions and design of nbgitpuller **will**
   surprise you in unexpected ways if you are pushing with git but pulling
   with nbgitpuller.
#. Your students are performing manual git operations on the git repository
   cloned as well as using nbgitpuller. Mixing manual git operations +
   automatic nbgitpuller operations is going to cause surprises on an ongoing
   basis, and should be avoided.

Installation
============

If you already have a JupyterHub, you can follow :ref:`these installation
instructions <install>` to install nbgitpuller there. They should also
work for installation on a local Jupyter Notebook installation without
JupyterHub.

If you do *not* have a JupyterHub, we recommend trying out `The Littlest
JupyterHub <https://tljh.jupyter.org>`_ to set one up. It comes built
in with nbgitpuller.

Using nbgitpuller as an instructor
==================================

Once installed, you create a specially crafted web link (called
*nbgitpuller links*) and send to your students via any method you like -
course website, LMS, email, etc. This link will contain at least the
following information:

#. The location of the JupyterHub you are sending them to.
#. The git repository where you have published your content.
#. Optionally, a particular file or directory you want to automatically
   open for your students once the repository has been synchronized. Note the entire repository will be copied, not just the specified file.

The first time a particular student clicks the link, a local copy of the
repository is made for the student. On successive clicks, the latest version
of the remote repository is fetched, and merged automatically with the
student's local copy using a :ref:`series of rules <topic/automatic-merging>`
that ensure students never get merge conflicts.

You can generate such *nbgitpuller links* with the `generator
<https://jupyterhub.github.io/nbgitpuller/link>`_.

There is also a video showing you how to use nbgitpuller

.. raw:: html

   <iframe
        width="560" height="315"
        src="https://www.youtube-nocookie.com/embed/o7U0ZuICVFg"
        frameborder="0"
        allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture"
        allowfullscreen>
   </iframe>

If you are interested in the details of available options when creating
the link, we have a :ref:`list of options <topic/url-options>` as well.

Full Contents
=============

.. toctree::
   :maxdepth: 2
 
   install
   contributing
   topic/automatic-merging
   topic/url-options
   link
