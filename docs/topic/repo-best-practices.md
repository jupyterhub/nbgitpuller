# Content git repository best practices

Sometimes, git's flexibility can lead to repositories that cause issues
when used with nbgitpuller. Here are some recommendations to make your
nbgitpuller experience smoother.


## Never force push

Never use `--force` or `--force-with-lease` when pushing to your repositories.
This is general good git practice, and unless you have [fairly deep
understanding](https://xkcd.com/1597/) of how git works, it might screw up some
of your users' local repositories beyond repair.

If you are using GitHub, you should enable [protected branches](https://docs.github.com/en/github/administering-a-repository/about-protected-branches)
to prevent accidental force pushes.

## Prevent your repos from becoming huge

Larger git repos increase chances of timeouts and other intermittent failures
that will be difficult to debug. They might leave your git repo in strange states
too - contents fetched but not checked out, half-fetched, etc. Try and keep it small -
under 100MB is great, under 1G is ok, but anything more is probably asking for trouble.

Large datasets are the biggest reason for increasing repository sizes. Try distribute
datasets some other way, use a subset of data, or compress your data if you need to.

## Don't add `.ipynb_checkpoints` (and similar files) to your git repo

Jupyter uses a hidden `.ipynb_checkpoints` directory to temporarily autosave copies of the
notebook. If you accidentally commit your local computer's copy of this to the git repo,
it can cause hard to debug issues when students click nbgitpuller links. The students'
Jupyter Notebook servers in the JupyterHub will also generate `.ipynb_checkpoints` for
autosaving, and conflicts between these two can cause issues. Similar issues can happen
with other temporary, hidden files - like `.DS_Store`, `__pycache__`, etc.

Adding `.ipynb_checkpoints` to your repo's `.gitignore` file will eliminate this
class of issues completely. `git add` and similar commands will no longer
accidentally include them in your repo. You can download this [python specific
gitignore](https://github.com/github/gitignore/blob/master/Python.gitignore)
file and put it in your repo as `.gitignore`, and it should take care of this.
