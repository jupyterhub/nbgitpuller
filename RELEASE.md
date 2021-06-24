# How to make a release

`nbgitpuller` is a package available on
[PyPI](https://pypi.org/project/nbgitpuller/) and
[conda-forge](https://anaconda.org/conda-forge/nbgitpuller).
These are instructions on how to make a release on PyPI.
The PyPI release is done automatically by TravisCI when a tag is pushed.


## Steps to make a release

1. Checkout main and make sure it is up to date.

   ```shell
   ORIGIN=${ORIGIN:-origin} # set to the canonical remote, e.g. 'upstream' if 'origin' is not the official repo
   git checkout main
   git fetch $ORIGIN main
   git reset --hard $ORIGIN/main
   # WARNING! This next command deletes any untracked files in the repo
   git clean -xfd
   ```

1. Set the `__version__` variable in
   [`nbgitpuller/version.py`](nbgitpuller/version.py)
   and make a commit.

   ```
   git add nbgitpuller/version.py
   VERSION=...  # e.g. 1.2.3
   git commit -m "release $VERSION"
   ```

1. Reset the `__version__` variable in
   [`nbgitpuller/version.py`](nbgitpuller/version.py)
   to an incremented patch version with a `dev` element, then make a commit.
   ```
   git add nbgitpuller/version.py
   git commit -m "back to dev"
   ```

1. Push your two commits to main.

   ```shell
   # first push commits without a tags to ensure the
   # commits comes through, because a tag can otherwise
   # be pushed all alone without company of rejected
   # commits, and we want have our tagged release coupled
   # with a specific commit in main
   git push $ORIGIN main
   ```

1. Create a git tag for the pushed release commit and push it.

   ```shell
   git tag -a $VERSION -m $VERSION HEAD~1

   # then verify you tagged the right commit
   git log

   # then push it
   git push $ORIGIN refs/tags/$VERSION
   ```

1. Following the release to PyPI, an automated PR should arrive to
   [conda-forge/nbgitpuller-feedstock](https://github.com/conda-forge/nbgitpuller-feedstock),
   check for the tests to succeed on this PR and then merge it to successfully
   update the package for `conda` on the `conda-forge` channel.
