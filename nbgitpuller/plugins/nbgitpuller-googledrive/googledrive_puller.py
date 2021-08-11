from nbgitpuller.hookspecs import hookimpl
import re
import asyncio
import aiohttp
from nbgitpuller.plugin_helper import handle_files_helper
from nbgitpuller import TEMP_DOWNLOAD_REPO_DIR

DOWNLOAD_URL = "https://docs.google.com/uc?export=download"


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
    loop = asyncio.get_event_loop()
    repo = query_line_args["repo"]
    query_line_args["download_q"].put_nowait("Determining type of archive...\n")
    response = loop.run_until_complete(get_response_from_drive(DOWNLOAD_URL, get_id(repo)))
    ext = determine_file_extension_from_response(response)
    query_line_args["download_q"].put_nowait(f"Archive is: {ext}\n")
    temp_download_file = f"{TEMP_DOWNLOAD_REPO_DIR}/download.{ext}"

    query_line_args["extension"] = ext
    query_line_args["dowload_func"] = download_archive_for_google
    query_line_args["dowload_func_params"] = query_line_args, temp_download_file

    tasks = handle_files_helper(query_line_args), query_line_args["progress_func"]()
    result_handle, _ = loop.run_until_complete(asyncio.gather(*tasks))
    return result_handle


def get_id(repo):
    """
    :param str repo: the url to the compressed file contained the google id
    :return the google drive id of the file to be downloaded
    :rtype str
    """
    start_id_index = repo.index("d/") + 2
    end_id_index = repo.index("/view")
    return repo[start_id_index:end_id_index]


def get_confirm_token(session, url):
    """
    :param aiohttp.ClientSession session: used to the get the cookies from the reponse
    :param str url : the url is used to filter out the correct cookies from the session
    :return the cookie if found or None if not found
    :rtype str

    This used to determine whether or not Google needs you to confirm a large download
    file is being downloaded
    """
    cookies = session.cookie_jar.filter_cookies(url)
    for key, cookie in cookies.items():
        if key.startswith('download_warning'):
            return cookie
    return None


async def download_archive_for_google(args, temp_download_file):
    """
    :param map args: key-value pairs includes repo path
    :param str temp_download_file: the path to save the requested file to

    This requests the file from the repo(url) given and saves it to the disk
    """
    yield "Downloading archive ...\n"
    try:
        repo = args["repo"]
        id = get_id(repo)
        CHUNK_SIZE = 1024
        async with aiohttp.ClientSession() as session:
            async with session.get(DOWNLOAD_URL, params={'id': id}) as response:
                token = get_confirm_token(session, repo)
                if token:
                    params = {'id': id, 'confirm': token}
                    response = await session.get(repo, params=params)
                with open(temp_download_file, 'ab') as fd:
                    count_chunks = 1
                    while True:
                        count_chunks += 1
                        if count_chunks % 1000 == 0:
                            display = count_chunks / 1000
                            yield f"Downloading Progress ... {display}MB\n"
                        chunk = await response.content.read(CHUNK_SIZE)
                        if not chunk:
                            break
                        fd.write(chunk)
        yield "Archive Downloaded....\n"
    except Exception as e:
        raise e


async def get_response_from_drive(url, id):
    """
    :param str url: the google download URL
    :param str id: the google id of the file to download
    :return response object
    :rtype json object
    You need to check to see that Google Drive has not asked the
    request to confirm that they disabled the virus scan on files that
    are bigger than 100MB(The size is mentioned online but I did not see
    confirmation - something larger essentially). For large files, you have
    to request again but this time putting the 'confirm=XXX' as a query
    parameter.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params={'id': id}) as response:
            token = get_confirm_token(session, url)
            if token:
                params = {'id': id, 'confirm': token}
                response = await session.get(url, params=params)
                return response
            return response


def determine_file_extension_from_response(response):
    """
    :param str response: the response object from the download
    :return the extension indicating the file compression(e.g. zip, tgz)
    :rtype str
    """
    content_disposition = response.headers.get('content-disposition')
    if content_disposition:
        fname = re.findall("filename\\*?=([^;]+)", content_disposition)
        fname = fname[0].strip().strip('"')
        ext = fname.split(".")[1]

    if ext is None:
        m = f"Could not determine compression type of: {content_disposition}"
        raise Exception(m)
    return ext
