import string
import os
import logging
import aiohttp
import asyncio
import subprocess
import shutil
from urllib.parse import urlparse
from functools import partial
from nbgitpuller import \
    TEMP_DOWNLOAD_REPO_DIR, \
    CACHED_ORIGIN_NON_GIT_REPO, \
    REPO_PARENT_DIR


async def execute_cmd(cmd, **kwargs):
    """
    :param array cmd: the commands to be executed
    :param json kwargs: potential keyword args included with command

    Call given command, yielding output line by line
    """
    yield '$ {}\n'.format(' '.join(cmd))
    kwargs['stdout'] = subprocess.PIPE
    kwargs['stderr'] = subprocess.STDOUT

    proc = subprocess.Popen(cmd, **kwargs)

    # Capture output for logging.
    # Each line will be yielded as text.
    # This should behave the same as .readline(), but splits on `\r` OR `\n`,
    # not just `\n`.
    buf = []

    def flush():
        line = b''.join(buf).decode('utf8', 'replace')
        buf[:] = []
        return line

    c_last = ''
    try:
        for c in iter(partial(proc.stdout.read, 1), b''):
            if c_last == b'\r' and buf and c != b'\n':
                yield flush()
            buf.append(c)
            if c == b'\n':
                yield flush()
            c_last = c
    finally:
        ret = proc.wait()
        if ret != 0:
            raise subprocess.CalledProcessError(ret, cmd)


async def initialize_local_repo(local_repo_path):
    """
    :param str local_repo_path: the locla path where the git repo is initialized

    Sets up the a local repo that acts like a remote; yields the
    output from the git init
    """
    yield "Initializing repo ...\n"
    logging.info(f"Creating local_repo_path: {local_repo_path}")
    os.makedirs(local_repo_path, exist_ok=True)
    async for e in execute_cmd(["git", "init", "--bare"], cwd=local_repo_path):
        yield e


async def clone_local_origin_repo(origin_repo_path, temp_download_repo):
    """
    :param str origin_repo_path: the local path we used to git init into
    :param str temp_download_repo: folder where the compressed archive
    is downloaded to

    Cloned the origin(which is local) to the folder, temp_download_repo.
    The folder, temp_download_repo, acts like the space where someone makes changes
    to master notebooks and then pushes the changes to origin. In other words,
    the folder, temp_download_repo, is where the compressed archive is downloaded,
    unarchived, and then pushed to the origin.
    """
    yield "Cloning repo ...\n"
    if os.path.exists(temp_download_repo):
        shutil.rmtree(temp_download_repo)
    logging.info(f"Creating temp_download_repo: {temp_download_repo}")
    os.makedirs(temp_download_repo, exist_ok=True)

    cmd = ["git", "clone", f"file://{origin_repo_path}", temp_download_repo]
    async for e in execute_cmd(cmd, cwd=temp_download_repo):
        yield e


def extract_file_extension(url):
    """
    :param str url: the url contains the extension we need to determine
    what kind of compression is used on the file being downloaded

    this is needed to unarchive various formats(eg. zip, tgz, etc)
    """
    u = urlparse(url)
    url_arr = u.path.split(".")
    if len(url_arr) >= 2:
        return url_arr[-1]
    raise Exception(f"Could not determine compression type of: {url}")


async def execute_unarchive(ext, temp_download_file, temp_download_repo):
    """
    :param str ext: extension used to determine type of compression
    :param str temp_download_file: the file path to be unarchived
    :param str temp_download_repo: where the file is unarchived to

    un-archives file using unzip or tar to the temp_download_repo
    """
    if ext == 'zip':
        cmd_arr = ['unzip', "-qo", temp_download_file, "-d", temp_download_repo]
    else:
        cmd_arr = ['tar', 'xzf', temp_download_file, '-C', temp_download_repo]
    async for e in execute_cmd(cmd_arr, cwd=temp_download_repo):
        yield e


async def download_archive(args, temp_download_file):
    """
    :param map args: key-value pairs including the aiohttp session object and repo path
    :param str temp_download_file: the path to save the requested file to

    This requests the file from the repo(url) given and saves it to the disk
    """
    yield "Downloading archive ...\n"
    try:
        CHUNK_SIZE = 1024
        async with args["client"] as session:
            async with session.get(args["repo"]) as response:
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
    except Exception as e:
        raise e

    yield "Archive Downloaded....\n"


async def push_to_local_origin(temp_download_repo):
    """
    :param str temp_download_repo: the current working directly of folder
    where the archive had been downloaded and unarchived

    The unarchived files are pushed back to the origin
    """
    async for e in execute_cmd(["git", "add", "."], cwd=temp_download_repo):
        yield e
    commit_cmd = [
        "git",
        "-c", "user.email=nbgitpuller@nbgitpuller.link",
        "-c", "user.name=nbgitpuller",
        "commit", "-q", "-m", "test", "--allow-empty"
    ]
    async for e in execute_cmd(commit_cmd, cwd=temp_download_repo):
        yield e
    async for e in execute_cmd(["git", "push", "origin", "master"], cwd=temp_download_repo):
        yield e


# this is needed becuase in handle_files_helper  I can not return
# from the async generator so it needs a global variable to hold the
# director name of the files downloaded
dir_names = None


async def handle_files_helper(args):
    """
    :param map args: key-value pairs including the repo, provider, extenstion,
    download function and download parameters in the case
    that the source needs to handle the download in a specific way(e.g. google
    requires a confirmation of the download)
    :return json object with the directory name of the download and
    the origin_repo_path
    :rtype json object

    This does all the heavy lifting in order needed to set up your local
    repos, origin, download the file, unarchiving and push the files
    back to the origin
    """
    url = args["repo"].translate(str.maketrans('', '', string.punctuation))
    provider = args["provider"]
    origin_repo = f"{REPO_PARENT_DIR}{CACHED_ORIGIN_NON_GIT_REPO}{provider}/{url}/"
    temp_download_repo = TEMP_DOWNLOAD_REPO_DIR
    temp_download_file = f"{TEMP_DOWNLOAD_REPO_DIR}/download.{args['extension']}"

    async def gener():
        global dir_names
        try:
            if not os.path.exists(origin_repo):
                async for i in initialize_local_repo(origin_repo):
                    yield i

            async for c in clone_local_origin_repo(origin_repo, temp_download_repo):
                yield c

            args["client"] = aiohttp.ClientSession()
            download_func = download_archive
            download_args = args, temp_download_file
            if "dowload_func" in args:
                download_func = args["dowload_func"]
                download_args = args["dowload_func_params"]

            async for d in download_func(*download_args):
                yield d

            async for e in execute_unarchive(args["extension"], temp_download_file, temp_download_repo):
                yield e

            os.remove(temp_download_file)
            async for p in push_to_local_origin(temp_download_repo):
                yield p

            unzipped_dirs = os.listdir(temp_download_repo)
            # name of the extracted directory
            dir_names = list(filter(lambda dir: ".git" not in dir and "__MACOSX" not in dir, unzipped_dirs))
            yield "\n\n"
            yield "Process Complete: Archive is finished importing into hub\n"
            yield f"The directory of your download is: {dir_names[0]}\n"
            shutil.rmtree(temp_download_repo)  # remove temporary download space
        except Exception as e:
            logging.exception(e)
            raise ValueError(e)

    try:
        async for line in gener():
            args["download_q"].put_nowait(line)
            await asyncio.sleep(0.1)
    except Exception as e:
        args["download_q"].put_nowait(e)
        raise e
    args["download_q"].put_nowait(None)
    return {"unzip_dir": dir_names[0], "origin_repo_path": origin_repo}
