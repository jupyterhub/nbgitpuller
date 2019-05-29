.. _topic/merging:

==========================
Automatic Merging Behavior
==========================

``nbgitpuller`` tries to make sure the end user who clicked the link
**never** has to manually interact with the git repo. This requires us to
make some opinionated choices on how we handle various cases where both the
student (end user) and instructor (author of the repo) repo have modified the
repository.

Here, how describe we handle the various possible cases each time the
student clicks the nbgitpuller link.

Case 1: Student and instructor changed different files
======================================================

The student's changes are left alone, and the instructor's changes are pulled
in to the local copy. Most common case. This is also what happens when the
instructor adds a new file / directory.

Case 2: Student & instructor changed different lines in same file
=================================================================

Very similar to case 1 - the student's changes are left alone, and the
instructor's changes are merged in to the existing local file.

Case 3: Student & instructor change same lines in same file
===========================================================

In this case, we **always keep the student's changes**. We want to never
accidentally lose a student's changes - ``nbgitpuller`` will not eat your
homework.

Case 4: Student deletes file locally, but instructor doesn't
============================================================

If the student has deleted a file locally, but the file is still present in
the remote repo, the file from the remote repo is pulled into the student's
directory. This enables the use case where a student wants to 'start over'
a file after having made many changes to it. They can simply delete the file,
click the nbgitpuller link again, and get a fresh copy.

Case 5: Student creates file manually, but instructor adds file with same name
==============================================================================

As an example, let's say the student manually creates a file named
``Untitled141.ipynb`` in the directory where nbgitpuller has pulled a
repository. At some point afterwards, the instructor creates a file *also*
named ``Untitled141.ipynb`` and pushes it to the repo.

When the student clicks the nbgitpuller link next, we want to make sure we
don't destroy the student's work. Since they were created in two different
places, the likelihood of them being mergeable is low. So we **rename** the
student's file, and pull the instructor's file. So the student's
``Untitled141.ipynb`` file will be renamed to
``Untitled141_<timestamp>.ipynb``, and the instructor's file will be kept at
``Untitled141.ipynb``.

This is a fairly rare case in our experience.
