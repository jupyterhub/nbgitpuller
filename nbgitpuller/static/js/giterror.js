export function GitError(gitsync, data) {
  const repo = gitsync.repo;
  const branch = gitsync.branch;
  const path = gitsync.targetpath;
  const url = new URL(window.location.href );

  
  if ("error" in data) {
    if (data.error.code == "merge") {
      url.searchParams.append("backup", "true");
      return MergeConflictHelp(data, path, url);
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
  return `<a href=${url} class="btn btn-primary role="button" style="margin-right: 5px" aria-label="Backup and resync, then go to Jupyter server.">Backup and resync</a>`
};

function MergeConflictHelp (data, path, url) {
  return `<p class="lead">${data.error.message}</p><p><strong>Backup and resync</strong> to backup the current state of your repository and sync updates into a new separate folder:<ul>
  <li><code>${path}_backup_YYYYMMDDHHMMSS</code> Timestamped backup folder containing the current state of your repository</li>
  <li><code>${path}</code> New folder containing updated content. <em>This new folder will not merge content from your backup due to the unresolvable conflicts.</em> You may want to manually copy backed up changes into the new folder.</li>
  </ul></p><p><strong>Proceed without syncing</strong> to continue with the current state of your repository without any new updates.</p><p><a href="https://nbgitpuller.readthedocs.io/en/latest/topic/automatic-merging.html">See more about automatic merging behavior.</a></p>
  ${ButtonBackupAndResync(url)}`;
};


function GeneralHelp (data) {
  return `<p class="lead">${data.error.message}</p>`
};
