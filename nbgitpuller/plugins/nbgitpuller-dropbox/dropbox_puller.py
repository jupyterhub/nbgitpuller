from nbgitpuller.plugin_helper import handle_files_helper
from nbgitpuller.plugin_helper import extract_file_extension
from nbgitpuller.hookspecs import hookimpl
import asyncio


def determine_file_extension(url):
    """
    :param str url: url to source
    :return the extension indicating the file compression(e.g. zip, tgz)
    :rtype str
    """
    return extract_file_extension(url)


@hookimpl
def handle_files(query_line_args):
    """
    :param json args: this includes any argument you put on the url
    PLUS the function, query_line_args["progress_func"], that writes messages to
    the progress stream in the browser window and the download_q,
    query_line_args["download_q"] the progress function uses.
    :return two parameter json unzip_dir and origin_repo_path
    :rtype json object
    """
    query_line_args["repo"] = query_line_args["repo"].replace("dl=0", "dl=1")  # dropbox: download set to 1
    ext = determine_file_extension(query_line_args["repo"])
    query_line_args["extension"] = ext

    loop = asyncio.get_event_loop()
    tasks = handle_files_helper(query_line_args), query_line_args["progress_func"]()
    result_handle, _ = loop.run_until_complete(asyncio.gather(*tasks))
    return result_handle
