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
def handle_files(repo_parent_dir, other_kw_args):
    """
    This function must be implemented by content-provider plugins in order to handle the downloading and decompression
    of a non-git sourced compressed archive.

    The repo_parent_dir is where you will save your downloaded archive

    The parameter, other_kw_args, contains all the arguments you put on the nbgitpuller URL link or passed to GitPuller
    via CLI. This allows you flexibility to pass information  your content-provider download plugin may need to
    successfully download source files.

    This function needs to return two pieces of information as a json object:
        - output_dir -- the is the name of the directory that will hold all the files you want GitPuller to expose
            for comparison, when git is the source, this is name of git repository you are pulling
        - origin_repo_path -- this is path to the local git repo that "acts" like the remote origin you would use
            if the content-provider is git.

    Once the files are saved to the directory, git puller can handle all the standard functions needed to make sure
    source files are updated or created as needed.

    I suggest you study the function handle_files_helper in file plugin_helper.py found in the
    nbgitpuller-downloader-plugins repository to get a deep sense of how
    we handle the downloading of compressed archives. There is also more documentation in the docs section of
    nbgitpuller. Finally, you can always implement the entire download process yourself and not use the
    handle_files_helper function but please to sure understand what is being passed into and back to the nbgitpuller
    handlers.

    :param str repo_parent_dir: save your downloaded archive here
    :param dict other_kw_args: this includes any argument you put on the nbgitpuller URL or pass via CLI as a dict
    :return two parameter json output_dir and origin_repo_path
    :rtype json object
    """
