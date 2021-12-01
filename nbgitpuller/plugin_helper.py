import string
import os
import logging
import aiohttp
import asyncio
import subprocess
import shutil
from urllib.parse import urlparse
from functools import partial
import tempfile

# this is the path to the local origin repository that nbgitpuller uses to mimic
# a remote repo in GitPuller
CACHED_ORIGIN_NON_GIT_REPO = ".nbgitpuller/targets/"


async def execute_cmd(cmd, **kwargs):
    """
    Call given command, yielding output line by line

    :param array cmd: the commands to be executed
    :param json kwargs: potential keyword args included with command
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
    Sets up the a local repo that acts like a remote; yields the
    output from the git init

    :param str local_repo_path: the locla path where the git repo is initialized
    """
    yield "Initializing repo ...\n"
    logging.info(f"Creating local_repo_path: {local_repo_path}")
    os.makedirs(local_repo_path, exist_ok=True)
    async for e in execute_cmd(["git", "init", "--bare"], cwd=local_repo_path):
        yield e


async def clone_local_origin_repo(origin_repo_path, temp_download_repo):
    """
    Cloned the origin(which is local) to the folder, temp_download_repo.
    The folder, temp_download_repo, acts like the space where someone makes changes
    to master notebooks and then pushes the changes to origin. In other words,
    the folder, temp_download_repo, is where the compressed archive is downloaded,
    unarchived, and then pushed to the origin.

    :param str origin_repo_path: the local path we used to git init into
    :param str temp_download_repo: folder where the compressed archive
    is downloaded to
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
    The file extension(eg. zip, tgz, etc) is extracted from the url to facilitate de-compressing the file
    using the correct application -- (zip, tar).

    :param str url: the url contains the extension we need to determine
    what kind of compression is used on the file being downloaded
    """
    u = urlparse(url)
    url_arr = u.path.split(".")
    if len(url_arr) >= 2:
        return url_arr[-1]
    raise Exception(f"Could not determine compression type of: {url}")


async def execute_unarchive(ext, temp_download_file, temp_download_repo):
    """
    un-archives file using unzip or tar to the temp_download_repo

    :param str ext: extension used to determine type of compression
    :param str temp_download_file: the file path to be unarchived
    :param str temp_download_repo: where the file is unarchived to
    """
    if ext == 'zip':
        cmd_arr = ['unzip', "-qo", temp_download_file, "-d", temp_download_repo]
    else:
        cmd_arr = ['tar', 'xzf', temp_download_file, '-C', temp_download_repo]
    async for e in execute_cmd(cmd_arr, cwd=temp_download_repo):
        yield e


async def download_archive(repo=None, temp_download_file=None):
    """
    This requests the file from the repo(url) given and saves it to the disk

    :param str repo: the git repo path
    :param str temp_download_file: the path to save the requested file to
    """
    yield "Downloading archive ...\n"
    try:
        CHUNK_SIZE = 1024
        async with aiohttp.ClientSession() as session:
            async with session.get(repo) as response:
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
    The unarchived files are pushed back to the origin

    :param str temp_download_repo: the current working directly of folder
    where the archive had been downloaded and unarchived
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


class HandleFilesHelper:
    """
    This class is needed to handle the use of dir_names inside the async generator as well as in the return object for
    the function handle_files_helper.
    """
    def __init__(self, helper_args, query_line_args):
        """
        This sets up the helper_args and query_line_args for use in the handle_files_helper and gener functions.

        :param dict helper_args: key-value pairs including the:
            - download_func download function
            - download_func_params download parameters in the case
                that the source needs to handle the download in a specific way(e.g. google
                requires a confirmation of the download)
            - extension (e.g. zip, tar) ] [OPTIONAL] this may or may not be included. If the repo name contains
                name of archive (e.g. example.zip) then this function can determine the extension for you; if not it
                needs to be provided.
        :param dict query_line_args:
            - repo,
            - provider,
            - repo_parent_dir
        :param helper_args:
        :param query_line_args:
        """
        self.dir_names = None
        self.url = query_line_args["repo"].translate(str.maketrans('', '', string.punctuation))
        self.content_provider = query_line_args["contentProvider"]
        self.repo = query_line_args["repo"]
        self.repo_parent_dir = helper_args["repo_parent_dir"]
        self.download_q = helper_args["download_q"]
        self.origin_repo = f"{self.repo_parent_dir}{CACHED_ORIGIN_NON_GIT_REPO}{self.content_provider}/{self.url}/"
        self.temp_download_dir = tempfile.TemporaryDirectory()

        # you can optionally pass the extension of your archive(e.g zip) if it is not identifiable from the URL file name
        # otherwise the extract_file_extension function will pull it off the repo name
        if "extension" not in helper_args:
            self.ext = extract_file_extension(query_line_args["repo"])
        else:
            self.ext = helper_args['extension']
        self.temp_download_file = f"{self.temp_download_dir.name}/download.{self.ext}"
        self.download_func = download_archive
        self.download_args = {
            "repo": self.repo,
            "temp_download_file": self.temp_download_file
        }

        # you can pass your own download function as well as download function parameters
        # if they are different from the standard download function and parameters. Notice I add
        # the temp_download_file to the parameters
        if "download_func" in helper_args:
            self.download_func = helper_args["download_func"]
        if "download_func_params" in helper_args:
            helper_args["download_func_params"]["temp_download_file"] = self.temp_download_file
            self.download_args = helper_args["download_func_params"]

    async def gener(self):
        """
        This does all the heavy lifting in the order needed to set up your local
        repos, origin, download the file, unarchive and push the files
        back to the origin
        """

        try:
            if not os.path.exists(self.origin_repo):
                async for i in initialize_local_repo(self.origin_repo):
                    yield i

            async for c in clone_local_origin_repo(self.origin_repo, self.temp_download_dir.name):
                yield c

            async for d in self.download_func(**self.download_args):
                yield d

            async for e in execute_unarchive(self.ext, self.temp_download_file, self.temp_download_dir.name):
                yield e

            os.remove(self.temp_download_file)
            async for p in push_to_local_origin(self.temp_download_dir.name):
                yield p

            unzipped_dirs = os.listdir(self.temp_download_dir.name)
            # name of the extracted directory
            self.dir_names = list(filter(lambda dir: ".git" not in dir and "__MACOSX" not in dir, unzipped_dirs))

            yield "\n\n"
            yield "Process Complete: Archive is finished importing into hub\n"
            yield f"The directory of your download is: {self.dir_names[0]}\n"

        except Exception as e:
            logging.exception(e)
            raise ValueError(e)
        finally:
            self.temp_download_dir.cleanup() # remove temporary download space

    async def handle_files_helper(self):
        """
        This calls the async generator function and handle the storing of messages from the gener() function
        into the download_q

        :return json object with the directory name of the download and
        the origin_repo_path
        :rtype json object
        """
        try:
            async for line in self.gener():
                self.download_q.put_nowait(line)
                await asyncio.sleep(0.1)
        except Exception as e:
            self.download_q.put_nowait(e)
            raise e
        # mark the end of the queue with a None value
        self.download_q.put_nowait(None)
        return {"output_dir": self.dir_names[0], "origin_repo_path": self.origin_repo}
