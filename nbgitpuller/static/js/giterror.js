export function GitError(message) {
  const s = message.toLowerCase();

  if (s.includes("merge"))
    return `<p class="lead">Unresolvable conflicts detected while syncing</p><p><strong>Proceed without syncing</strong> to continue with the current state of your repository with no updates.</p><p><strong>Backup and resync</strong> to backup the current state of your repository (renamed with a timestamp) and pull in a fresh copy of the source content into a new folder (named with no timestamp).</p>`;
}