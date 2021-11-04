# nbgitpuller - dropbox download plugin

Dropbox file/folder names add the dl=0 URL query parameter to their URLs.

This plugin expects the URL to look like this:
- https://www.dropbox.com/s/qou3g7hf41vq6sw/materials-sp20-external.zip?dl=0

This plugin replaces dl=0 with dl=1 and then downloads the file.

Please note that the file(compressed archive) must have permissions set so that anyone
with the link can view the file.

## Installation

```shell
python3 -m pip install nbgitpuller-dropbox
```


