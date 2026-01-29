export function GitError(gitsync, data) {
  const repo = gitsync.repo;
  const branch = gitsync.branch;
  const path = gitsync.targetpath;
  const url = new URL(window.location.href );

  if ("error" in data) {
    switch (data.error.code) {
      case "merge":
        url.searchParams.append("backup", "true");
        return MergeConflictHelp(data, path, url);
      case "branch_exist":
        return BranchExistHelp(data, repo, branch)
      case "branch_resolve":
        return BranchResolveHelp(data, repo)
      case "ls_remote":
        return RemoteHelp(data, repo)
      default:
        return GeneralHelp()
    }
  } else {
    data.error ??= {};
    data.error.message ??= "Error detected";
    return GeneralHelp()
  }
  ;
};

function ButtonBackupAndResync(url) {
  const a = document.createElement("backup-button")
  a.ref = url;
  a.className = "btn btn-primary";
  a.role = "button";
  a.style.marginRight = "5px";
  a.textContent = "Backup and resync";
  a.setAttribute(
    "aria-label",
    "Backup and resync, then go to Jupyter server."
  );
  return a;
};

function MergeConflictHelp (data, path, url) {
  return {
    body: `<p class="lead">${data.error.message}</p><p><strong>Backup and resync</strong> to backup the current state of your repository and sync updates into a new separate folder:<ul>
    <li><code>${path}_backup_YYYYMMDDHHMMSS</code> Timestamped backup folder containing the current state of your repository</li>
    <li><code>${path}</code> New folder containing updated content. <em>This new folder will not merge content from your backup due to the unresolvable conflicts.</em> You may want to manually copy backed up changes into the new folder.</li>
    </ul></p>`,
    button: ButtonBackupAndResync(url)
  }
};

function BranchExistHelp (data, repo, branch) {
  return {
    body: `<p class="lead">${data.error.message}</p><p>The link author provided an incorrect branch name, <code>${branch}</code>, for the source content hosted at URL <a href=${repo}>${repo}</a>. Check with the link author that the URL is valid and that the nbgitpuller link has the correct branch name.</p>`}
};

function BranchResolveHelp (data, repo) {
  return {
    body: `<p class="lead">${data.error.message}</p><p>The link author did not provide a branch name for the source content hosted at URL <a href=${repo}>${repo}</a>, and no other branches could be found. Check with the link author that the URL is valid and ask them to provide an nbgitpuller link with the correct branch name.</p></p>`}
};

function RemoteHelp (data, repo) {
  return {
    body: `<p class="lead">${data.error.message}</p><p>The source content <a href=${repo}>${repo}</a> is unavailable.</p><p>This can be caused by:<ul><li>An invalid nbgitpuller link<ul><li>The source content could be private. This means you are not authorized to access the repository. This leads to a HTTP 403 "Forbidden" error. Check with the link author who can grant public access to the source content.</li><li>The source content might not exist. This leads to a HTTP 404 "Not Found" error. Check with the link author that the source content exists, or if there is a typo in the source content repository link.</li></ul></li><li>Network issues<ul><li>Network issues can be caused by your internet service provider, your router device or your local machine's network settings. Check your local connection.</li><li>The service hosting the source content could be experiencing difficulties. This can lead to a HTTP 50x server error. Check the status page of the service, e.g. <a href="https://www.githubstatus.com/">GitHub status</a>, for the latest news on any incidents.</li></ul></li></ul></p>`}
}

function GeneralHelp () {
  return {
    body: `<p class="lead">An unexpected error occurred</p><p>Contact the link author and share the error log with them to help diagnose the problem using the "Copy error to clipboard" button above.</p>`}
};
