export function GitError(gitsync, data, buttonDiv) {
  const repo = gitsync.repo;
  const branch = gitsync.branch;
  const path = gitsync.targetpath;
  const url = new URL(window.location.href );

  console.log(data)
  
  if ("error" in data) {
    if (data.error.code == "merge") {
      url.searchParams.append("backup", "true");
      return MergeConflictHelp(data, path, url, buttonDiv);
    } else if (data.error.code == "branch_exist") {
      return BranchExistHelp(data, repo, branch)
    } else {
      return GeneralHelp(data)
    }
  } else {
    data.error ??= {};
    data.error.message ??= "Error detected";
    return GeneralHelp(data)
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

function MergeConflictHelp (data, path, url, buttonDiv) {
  buttonDiv.prepend(ButtonBackupAndResync(url));
  return `<p class="lead">${data.error.message}</p><p><strong>Backup and resync</strong> to backup the current state of your repository and sync updates into a new separate folder:<ul>
    <li><code>${path}_backup_YYYYMMDDHHMMSS</code> Timestamped backup folder containing the current state of your repository</li>
    <li><code>${path}</code> New folder containing updated content. <em>This new folder will not merge content from your backup due to the unresolvable conflicts.</em> You may want to manually copy backed up changes into the new folder.</li>
    </ul></p>`;
};

function BranchExistHelp (data, repo, branch) {
  return `<p class="lead">${data.error.message}</p><p>The link author provided an incorrect branch name, <code>${branch}</code>, for the source content hosted at URL <a href=${repo}>${repo}</a>. Check with the link author that the URL is valid and that the nbgitpuller link has the correct branch name.</p>`
};

function GeneralHelp (data) {
  return `<p class="lead">${data.error.message}</p>`
};
