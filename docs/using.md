# Using nbgitpuller

This page covers some of the common reasons and ways to use nbgitpuller.

## When to use nbgitpuller

You should use nbgitpuller when:

1. You are running a JupyterHub for a class & want an easy way to distribute materials to
   your students without them having to understand what git is.
2. You have a different out of band method for collecting completed assignments / notebooks
   from students, since they can not just 'push it back' via git.

You should *not* use this when:

1. You are an instructor using a JupyterHub / running notebooks locally to create materials
   and push them to a git repository. You should just use git directly, since the assumptions
   and design of nbgitpuller **will** surprise you in unexpected ways if you are pushing with
   git but pulling with nbgitpuller.
2. Your students are performing manual git operations on the git repository cloned as well as
   using nbgitpuller. Mixing manual git operations + automatic nbgitpuller operations is going
   to cause surprises on an ongoing basis, and should be avoided.

## How to use nbgitpuller

1. Visit the nbgitpuller link generator at https://jupyterhub.github.io/nbgitpuller/link.html.
2. Enter the IP address or URL to your JupyterHub. Include http:// or https:// as appropriate.
3. Enter an alternative URL path if desired. If not set, the generated link will take users to the default hub url, however this can be changed. For example specifying "lab" will launch JupyterLab if installed. Entering "path/to/a/notebook.ipynb" will open that notebook.
4. Enter the URL to your Git repository. This can reference any Git service provider such as GitHub, GitLab, or a local instance.
5. If your git repository is using a non-default branch name, you can specify that under branch. Most people do not need to customize this.

The link printed at the bottom of the form can be distributed to users. You can also click it to test that it is working as intended, and adjust the form values until you get something you are happy with.

To preseed the form, append query string arguments to the link generator itself, for example https://jupyterhub.github.io/nbgitpuller/link?hub=http://jupyterhub.example.com. This may be useful when you want to suggest initial values to someone else. The other parameters are `urlpath`, `repo`, and `branch`. Resetting the form will remove the seeded values and re-enable the form fields.

# Git clone destination

Git repositories are cloned into the default working directory.
You can specify a different parent directory for the clone by setting the environment variable `NBGITPULLER_PARENTPATH`, this should be relative to the working directory.
If you require full control over the destination directory, or want to set the directory at runtime in the nbgitpuller link use the `targetPath` parameter.

## Using the command line interface

It is also possible to use `nbgitpuller` from the command line. For example,
here's how to synchronize the repository listed above using the command line:

```
gitpuller https://github.com/data-8/materials-fa17 master my_materials_fa17
```

This will synchronize the `master` branch of the repository to a folder
called `my_materials_fa17`.

See the command line help for more information.
