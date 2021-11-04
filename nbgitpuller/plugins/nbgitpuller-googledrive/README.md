# nbgitpuller - google drive download plugin

Google Drive uses a uniquely formatted URL to identify files and folders. As a result,
programmatically downloading from Google Drive requires special handling. The
implementation of the download plugin for Google Drive handles these requirements.

The plugin is expecting a URL in this format:
- https://drive.google.com/file/d/1p3m0h5UGWdLkVVP0SSJH6j1HpG2yeDlU/view?usp=sharing

Please note that the file(compressed archive) must have permissions set so that anyone
with the link can view the file.

## Installation

```shell
python3 -m pip install nbgitpuller-googledrive
```
