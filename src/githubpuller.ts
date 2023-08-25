import { PathExt } from "@jupyterlab/coreutils";
import { IFileBrowserFactory } from "@jupyterlab/filebrowser";
import { Contents } from "@jupyterlab/services";

export class GithubPuller {
  constructor(options: Private.IOptions) {
    this._browserFactory = options.browserFactory;
    this._contents = options.contents;
  }

  async clone(url: string, branch: string): Promise<string> {
    const basePath = PathExt.basename(url);
    await this._createTree([basePath]);

    const fetchUrl = `${url}/git/trees/${branch}?recursive=true`;
    const fileList = await fetch(fetchUrl, {
      method: "GET",
      headers: {
        Accept: "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "request",
      },
    })
      .then((resp) => resp.json())
      .then((data) => data.tree as any[]);

    const directories = Object.values(fileList)
      .filter((fileDesc) => fileDesc.type === "tree")
      .map((directory) => directory.path as string);

    const files = Object.values(fileList).filter(
      (fileDesc) => fileDesc.type === "blob",
    );

    const errors = new Map<string, string[]>();
    await this._createTree(directories, basePath).then(async () => {
      for (const file of files) {
        const uploadError = await this._getFile(url, file.path, branch, basePath);
        if (uploadError) {
          const files = errors.get(uploadError.type) || [];
          errors.set(uploadError.type, [...files, uploadError.file]);
        }
      }
    });
    errors.forEach((value, key) => {
      console.warn(
        `The following files have not been uploaded.\nCAUSE: ${key}\nFILES: `, value
      );
    });

    return basePath;
  }

  private async _createTree(
    directories: string[],
    basePath: string = null,
  ): Promise<void> {
    directories.sort();
    for (let directory of directories) {
      directory = basePath ? PathExt.join(basePath, directory) : directory;
      const options = {
        type: "directory" as Contents.ContentType,
        path: PathExt.dirname(directory),
      };
      // Create directory if it does not exist.
      await this._contents.get(directory, { content: false }).catch(() => {
        this._contents.newUntitled(options).then(async (newDirectory) => {
          await this._contents.rename(newDirectory.path, directory);
        });
      });
    }
  }

  private async _getFile(
    url: string,
    fileUrl: string,
    branch: string,
    basePath: string = null,
  ): Promise<void | Private.uploadError> {
    const filePath = basePath ? PathExt.join(basePath, fileUrl) : fileUrl;

    // do not upload existing file.
    let fileExist = false;
    await this._contents.get(filePath, { content: false })
      .then(() => {
        fileExist = true;
      })
      .catch(() => undefined);

    if (fileExist) {
      return {
        type: 'File already exist',
        file: filePath
      };
    }

    // Upload missing files.
    const { defaultBrowser: browser } = this._browserFactory;
    const fetchUrl = `${url}/contents/${fileUrl}?ref=${branch}`;
    const downloadUrl = await fetch(fetchUrl, {
      method: "GET",
      headers: {
        Accept: "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "request",
      },
    })
      .then((resp) => resp.json())
      .then((data) => data.download_url);

    const resp = await fetch(downloadUrl);
    const blob = await resp.blob();
    const type = resp.headers.get("Content-Type") ?? "";

    let filename = PathExt.basename(fileUrl);
    let inc = 0;
    let uniqueFilename = false;

    while (!uniqueFilename) {
      await this._contents
        .get(filename, { content: false })
        .then(() => {
          filename = `${filename}_${inc}`;
          inc++;
        })
        .catch((e) => {
          uniqueFilename = true;
        });
    }

    const file = new File([blob], filename, { type });
    await browser.model.upload(file).then(async (model) => {
      if (!(model.path === filePath)) {
        await this._contents.rename(model.path, filePath);
      }
    });
  }

  private _browserFactory: IFileBrowserFactory;
  private _contents: Contents.IManager;
}

namespace Private {
  export interface IOptions {
    browserFactory: IFileBrowserFactory;
    contents: Contents.IManager;
  }

  export interface uploadError {
    type: string;
    file: string;
  }
}
