import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin,
} from "@jupyterlab/application";
import { PathExt } from "@jupyterlab/coreutils";
import { IFileBrowserFactory } from "@jupyterlab/filebrowser";
import { GithubPuller } from "./githubpuller";

const assignmentListExtension: JupyterFrontEndPlugin<void> = {
  id: "nbgitpuller.plugin",
  autoStart: true,
  requires: [IFileBrowserFactory],
  activate: (app: JupyterFrontEnd, browserFactory: IFileBrowserFactory) => {
    if (!(app.name === "JupyterLite")) {
      return;
    }

    const urlParams = new URLSearchParams(window.location.search);
    const repo = urlParams.get("repo");

    if (!repo) {
      return;
    }

    const branch = urlParams.get("branch") || "main";
    let filePath = urlParams.get("urlpath");

    const repoUrl = new URL(repo);
    repoUrl.hostname = "api.github.com";
    repoUrl.pathname = `/repos${repoUrl.pathname}`;

    // TODO: delete the following line as soon as a dedicated url generator is available.
    filePath =
      "/" +
      PathExt.relative(`tree/${PathExt.basename(repoUrl.href)}`, filePath);

    const puller = new GithubPuller({
      browserFactory: browserFactory,
      contents: app.serviceManager.contents,
    });

    puller.clone(repoUrl.href, branch).then(async (basePath) => {
      // FIXME: the file does not exist yet !!
      app.commands.execute("filebrowser:open-path", {
        path: PathExt.join(basePath, filePath),
      });
    });
  },
};

export default assignmentListExtension;
