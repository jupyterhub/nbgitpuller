import subprocess
import os
import logging
import requests
from requests_file import FileAdapter
import shutil
import re


# for large files from Google Drive
def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value
    return None


# sets up the a local repo that acts like a remote
def initialize_local_repo(local_repo_path):
    logging.info(f"Creating local_repo_path: {local_repo_path}")
    os.makedirs(local_repo_path, exist_ok=True)

    subprocess.check_output(["git", "init", "--bare"], cwd=local_repo_path)


# local repo cloned from the "remote" which is in user drive
def clone_local_origin_repo(origin_repo_path, temp_download_repo):
    logging.info(f"Creating temp_download_repo: {temp_download_repo}")
    os.makedirs(temp_download_repo, exist_ok=True)

    cmd = ["git", "clone", f"file://{origin_repo_path}", temp_download_repo]
    subprocess.check_output(cmd, cwd=temp_download_repo)


# this is needed to unarchive various formats(eg. zip, tgz, etc)
def determine_file_extension(url, response):
    file_type = response.headers.get('content-type')
    content_disposition = response.headers.get('content-disposition')
    ext = None
    if content_disposition:
        fname = re.findall("filename\\*?=([^;]+)", content_disposition)
        fname = fname[0].strip().strip('"')
        ext = fname.split(".")[1]
    elif file_type and "/zip" in file_type:
        ext = "zip"
    else:
        url = url.split("/")[-1]
        if "?" in url:
            url = url[0:url.find('?')]
        if "." in url:
            ext = url.split(".")[1]

    if not ext:
        m = f"Could not determine the file extension for unarchiving: {url}"
        raise Exception(m)
    return ext


# the downloaded content is in the response -- unarchive and save to the disk
def save_response_content(url, response, temp_download_repo):
    try:
        ext = determine_file_extension(url, response)
        CHUNK_SIZE = 32768
        temp_download_file = f"{temp_download_repo}/download.{ext}"
        with open(temp_download_file, "wb") as f:
            for chunk in response.iter_content(CHUNK_SIZE):
                # filter out keep-alive new chunks
                if chunk:
                    f.write(chunk)

        shutil.unpack_archive(temp_download_file, temp_download_repo)

        os.remove(temp_download_file)
    except Exception as e:
        m = f"Problem handling file download: {str(e)}"
        raise Exception(m)


# grab archive file from url
def fetch_files(url, id=-1):
    session = requests.Session()
    session.mount('file://', FileAdapter())  # add adapter for pytests
    response = session.get(url, params={'id': id}, stream=True)
    token = get_confirm_token(response)
    if token:
        params = {'id': id, 'confirm': token}
        response = session.get(url, params=params, stream=True)

    return response


# this drive the file handling -- called from zip_puller by all the
# handle_files implementations for GoogleDrive, Dropbox, and standard
# Web url
def handle_files_helper(args):
    try:
        origin_repo = args["repo_parent_dir"] + args["origin_dir"]
        temp_download_repo = args["repo_parent_dir"] + args["download_dir"]
        if os.path.exists(temp_download_repo):
            shutil.rmtree(temp_download_repo)

        if not os.path.exists(origin_repo):
            initialize_local_repo(origin_repo)

        clone_local_origin_repo(origin_repo, temp_download_repo)
        save_response_content(args["repo"], args["response"], temp_download_repo)
        subprocess.check_output(["git", "add", "."], cwd=temp_download_repo)
        subprocess.check_output(["git", "-c", "user.email=nbgitpuller@nbgitpuller.link", "-c", "user.name=nbgitpuller", "commit", "-m", "test", "--allow-empty"], cwd=temp_download_repo)
        subprocess.check_output(["git", "push", "origin", "master"], cwd=temp_download_repo)
        unzipped_dirs = os.listdir(temp_download_repo)

        dir_names = list(filter(lambda dir: ".git" not in dir, unzipped_dirs))
        return {"unzip_dir": dir_names[0], "origin_repo_path": origin_repo}
    except Exception as e:
        logging.exception(e)
        raise ValueError(e)
