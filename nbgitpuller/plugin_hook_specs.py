import pluggy

# this hookspec is decorating the handle_files function below. The decorator defines
# the interface(hook specifications) for any implementing content-provider plugins. The project name, nbgitpuller,
# is passed to the constructor for HookspecMarker and HookimplMarker as well as to the constructor for the
# PluginManager in handlers.py in order to allow the PluginManager.add_hookspecs method to automatically discover
# all marked functions.
hookspec = pluggy.HookspecMarker("nbgitpuller")

# As a convenience the hookimpl field can be used by content-provider plugins to decorate the implementations of the
# handle_files function. A content-provider plugin could create the HookImplMarker itself but in order to register
# with the PluginManager the name('nbgitpuller') must be used as we do here.
hookimpl = pluggy.HookimplMarker("nbgitpuller")


@hookspec(firstresult=True)
def handle_files(helper_args, query_line_args):
    """
    :param json helper_args: these keyword args are passed from the main thread of nbgitpuller and include:
        - repo_parent_dir: save your downloaded archive here
        - wait_for_sync_progress_queue:
            A partial function with an infinite loop continuously checking the download_q for messages to show the
            user in the UI.
        - download_q:
            This is a Queue that accepts messages to be displayed in the UI. You might tell the user what percent of
            the download is complete or any other progress that might inform the user.
    :param json query_line_args: this includes any argument you put on the nbgitpuller URL
    :return two parameter json unzip_dir and origin_repo_path
    :rtype json object

    This function must be implemented by content-provider plugins in order to handle the downloading and decompression
    of a non-git sourced compressed archive.

    The helper_args contain three keyword arguments that are necessary to successfully save a
    compressed archive:
        - repo_parent_dir: save your downloaded archive here
        - wait_for_sync_progress_queue:
            A partial function with an infinite loop continuously checking the download_q for messages to show the
            user in the UI.
        - download_q:
            This is a Queue that accepts messages to be displayed in the UI. You might tell the user what percent of
            the download is complete or any other progress that might inform the user.to a user's jupyterhub home drive.

    The parameter, query_line_args, contains all the arguments you put on the nbgitpuller URL link. This allows you
    flexibility to pass information your content-provider download plugin may need to successfully download
    source files.

    This function needs to return two pieces of information as a json object:
        - unzip_dir -- the is the name of the folder you unzipped the archive into
        - origin_repo_path -- this is path to the local git repo that "acts" like the remote origin you would use
            if the content-provider is git.

    Once the files are saved to the directory, git puller can handle all the standard functions needed to make sure
    source files are updated or created as needed.

    I suggest you study the function handle_files_helper in the plugin_helper.py file to get a deep sense of how
    we handle the downloading of compressed archives. There is also more documentation in the docs section of
    nbgitpuller. Finally, you can always implement the entire download process yourself and not use the
    handle_files_helper function but please to sure understand what is being passed into and back to the nbgitpuller
    handlers.
    """
