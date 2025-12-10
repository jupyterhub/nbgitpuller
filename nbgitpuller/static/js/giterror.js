export function GitError(gitsync, message) {
  const s = message.toLowerCase();
  const repo = gitsync.repo;
  const branch = gitsync.branch;
  const path = gitsync.targetpath;
  const url = new URL(window.location.href );
  url.searchParams.append("backup", "true");

  if (s.includes("merge"))
    return `<p class="lead">Unresolvable conflicts detected while syncing</p><p><strong>Proceed without syncing</strong> to continue with the current state of your repository without updates.</p><p><strong>(Recommended) Backup and resync</strong> to backup the current state of your repository and sync updates into a new separate folder:<ul>
    <li><code>${path}_backup_YYYY-MM-DD_HH:MM:SS</code> Timestamped backup folder containing the current state of your repository</li>
    <li><code>${path}</code> New folder containing updated content. This will not merge content from your backup due to the unresolvable conflicts. You may want to manually copy backed up changes into the new folder.</li>
    </ul></p>
    <a href=${url} class="btn btn-default role="button" style="margin-top: 6px;"aria-label="Backup and resync, then go to Jupyter server.">Backup and resync</a>`;
}