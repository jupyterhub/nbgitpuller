import pluggy

hookspec = pluggy.HookspecMarker("nbgitpuller")
hookimpl = pluggy.HookimplMarker("nbgitpuller")


@hookspec(firstresult=True)
def handle_files(query_line_args):
    """
    :param json query_line_args: this includes any argument you put on the url
    :return two parameter json unzip_dir and origin_repo_path
    :rtype json object

    The developer uses this function to download, un-compress and save the
    source files to the TEMP_DOWNLOAD_REPO_DIR folder.

    The parameter, query_line_args, is any argument you put on the URL

    Once the files are saved to the directly, git puller can handle all the
    standard functions needed to make sure source files are updated or created
    as needed.
    """
