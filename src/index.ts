import { JupyterFrontEnd, JupyterFrontEndPlugin } from "@jupyterlab/application";
import { IFileBrowserFactory } from "@jupyterlab/filebrowser";
import { GithubPuller } from "./githubpuller";

const assignmentListExtension: JupyterFrontEndPlugin<void> = {
  id: 'nbgitpuller.plugin',
  autoStart: true,
  requires: [IFileBrowserFactory],
  activate: (
    app: JupyterFrontEnd,
    browserFactory: IFileBrowserFactory
  ) => {
    const puller = new GithubPuller({
      browserFactory: browserFactory,
      contents: app.serviceManager.contents
    });

    puller.clone('https://api.github.com/repos/brichet/testing-repo');
  }
}

export default assignmentListExtension;
