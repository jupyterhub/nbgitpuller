import pluggy

hookspec = pluggy.HookspecMarker("nbgitpuller")


@hookspec
def handle_files(self, repo, repo_parent_dir):
    """
    :param str repo: download url to source
    :param str repo_parent_dir: where we will store the downloaded repo
    :return two parameter json unzip_dir and origin_repo_path
    :rtype json object
    This handles the downloading of non-git source
    files into the user directory. Once downloaded,
    the files are merged into a local git repository.

    Once the local git repository is updated(or created
    the first time), git puller can then handle this
    directory as it would sources coming from a
    git repository.
    """
