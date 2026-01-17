function ButtonBackupAndResync(url) {
  return `<a href=${url} class="btn btn-primary role="button" style="margin-right: 5px" aria-label="Backup and resync, then go to Jupyter server.">Backup and resync</a>`
};

export function GitError(gitsync, message) {
  const s = message.toLowerCase();
  const repo = gitsync.repo;
  const branch = gitsync.branch;
  const path = gitsync.targetpath;
  const url = new URL(window.location.href );

  console.log(s)

  if (s.includes("merge")) {
    url.searchParams.append("backup", "true");
    return `<p class="lead">Unresolvable conflicts detected while syncing</p><p><strong>Backup and resync</strong> to backup the current state of your repository and sync updates into a new separate folder:<ul>
    <li><code>${path}_backup_YYYYMMDDHHMMSS</code> Timestamped backup folder containing the current state of your repository</li>
    <li><code>${path}</code> New folder containing updated content. <em>This new folder will not merge content from your backup due to the unresolvable conflicts.</em> You may want to manually copy backed up changes into the new folder.</li>
    </ul></p><p><a href="https://nbgitpuller.readthedocs.io/en/latest/topic/automatic-merging.html">See more about automatic merging behavior.</a></p>${ButtonBackupAndResync(url)}`;
  } else if (s.includes("ls-remote")) {
    return `<p class="lead">Content unavailable</p><p>The source content <a href=${repo}>${repo}</a> is unavailable.</p><p>This can be caused by:<ul><li>An invalid nbgitpuller link<ul><li>The source content could be private. This means you are not authorized to access the repository. This leads to a HTTP 403 "Forbidden" error. Check with the link author who can grant public access to the source content.</li><li>The source content might not exist. This leads to a HTTP 404 "Not Found" error. Check with the link author that the source content exists, or if there is a typo in the source content repository link.</li></ul></li><li>Network issues<ul><li>Network issues can be caused by your internet service provider, your router device or your local machine's network settings. Check your local connection.</li><li>The service hosting the source content could be experiencing difficulties. This can lead to a HTTP 50x server error. Check the status page of the service, e.g. <a href="https://www.githubstatus.com/">GitHub status</a>, for the latest news on any incidents.</li></ul></li></ul></p>`
  } else if (s.includes("problem accessing head branch")) {
    return `<p class="lead">Branch name unresolved</p><p>The link author did not provide a branch name for the source content hosted at URL <a href=${repo}>${repo}</a>, and no other branches could be found. Check with the link author that the source content repository URL is valid and update the nbgitpuller link with the correct branch name.</p>`
  } else if (s.includes("not found in repo")) {
    return `<p class="lead">Branch name not found</p><p>The link author provided an incorrect branch name for the source content hosted at URL <a href=${repo}>${repo}</a>. Check with the link author that the source content repository URL is valid and update the nbgitpuller link with the correct branch name.</p>`
  };
};
