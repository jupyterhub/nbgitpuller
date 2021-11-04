# nbgitpuller - standard web server download plugin

The standard web server download plugin handles any publicly accessible URL that points
by name to the compressed archive; this is in contrast to URLs that point to compressed archives stored in
services like Google Drive or Dropbox.

In these services, the URL uses the services mechanism for determining
the compressed file(eg. an ID that identifies the file rather than the name of the file itself)
and hence the downloading from these services is slightly different. I have provided
examples in the folders nbgitpuller-dropbox and nbgitpuller-googledrive.

The format of the URL is like any standard web address. For example:
- https://github.com/username/folder/raw/master/materials-sp20-external.tgz
- https://myinstituition.edu/courseX/x-materials.zip

## Installation

```shell
python3 -m pip install nbgitpuller-standard
```
