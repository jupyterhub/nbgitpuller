export function GitError(message) {
  const s = message.toLowerCase();

  if (s.includes("merge"))
    return `<p class="lead">Unresolvable conflicts detected while syncing</p><p><strong>Proceed without syncing</strong> to continue with the current state of your repository without updates.</p><p><strong>(Recommended) Backup and resync</strong> to backup the current state of your repository and sync updates into a new separate folder:<dl class="dl-horizontal">
    <dt><code>backup folder name</code></dt>
    <dd>Backup folder containing the current state of your repository</dd>
    <dt><code>new folder name</code></dt>
    <dd>New folder containing updated content. This will not merge content from your backup due to the unresolvable conflicts. You may want to manually copy across your work into the new folder.</dd>
    </dl></p>`;
}