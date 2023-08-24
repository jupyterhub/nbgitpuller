import { PathExt } from '@jupyterlab/coreutils';
import { IFileBrowserFactory } from '@jupyterlab/filebrowser';
import { Contents } from "@jupyterlab/services";


export class GithubPuller{
  constructor(options: Private.IOptions){
    this._browserFactory = options.browserFactory;
    this._contents = options.contents;
  }

  async clone(url: string): Promise<void> {
    const mainPath = PathExt.basename(url);
    await this._createTree([mainPath]);

    const fetchUrl = `${url}/git/trees/main?recursive=true`;
    const fileList = await fetch(
      fetchUrl,
      {
        method: "GET",
        headers:{
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28',
            'User-Agent': 'request'
        }
      })
      .then(resp => resp.json())
      .then(data => data.tree as any[]);

    const directories = Object.values(fileList)
      .filter(fileDesc => fileDesc.type === 'tree')
      .map(directory => directory.path as string);

    const files = Object.values(fileList)
      .filter(fileDesc => fileDesc.type === 'blob');

    this._createTree(directories, mainPath)
      .then(async () => {
        for (const file of files) {
          await this._getFile(url, file.path, mainPath);
        }
      });
  }

  private async _createTree(directories: string[], mainPath: string = null) {
    directories.sort();
    for (let directory of directories) {
      directory = mainPath ? PathExt.join(mainPath, directory) : directory
      const options = {
        type: 'directory' as Contents.ContentType,
        path: PathExt.dirname(directory)
      };
      // Create directory if it does not exist.
      await this._contents.get(directory, {content:false})
        .catch(() => {
          this._contents.newUntitled(options)
          .then(async newDirectory => {
            await this._contents.rename(newDirectory.path, directory);
          });
        });
    }
  }

  private async _getFile(url:string, filePath: string, mainPath: string = null) {
    const { defaultBrowser: browser } = this._browserFactory;
    const fetchUrl = `${url}/contents/${filePath}`;
    const downloadUrl = await fetch(
      fetchUrl,
      {
        method: "GET",
        headers:{
          'Accept': 'application/vnd.github+json',
          'X-GitHub-Api-Version': '2022-11-28',
          'User-Agent': 'request'
        }
      })
      .then(resp => resp.json())
      .then(data => data.download_url);

    const resp = await fetch(downloadUrl);
    const blob = await resp.blob();
    const type = resp.headers.get('Content-Type') ?? '';

    let filename = PathExt.basename(filePath);
    let inc = 0;
    let uniqueFilename = false;

    while (!uniqueFilename) {
      await this._contents.get(filename, {content:false})
        .then(() => {
          filename = `${filename}_${inc}`
          inc ++;
        })
        .catch((e) => {
          uniqueFilename = true;
        });
    }

    const file = new File([blob], filename, {type});
    await browser.model.upload(file)
      .then(async model => {
        filePath = mainPath ? PathExt.join(mainPath, filePath) : filePath
        if (!(model.path === filePath)){
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
  };
}
