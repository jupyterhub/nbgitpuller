# Frequently asked questions

## Can I automatically tell JupyterHub what kind of server to start (node size, profile name, etc) as part of my nbgitpuller link?

You can use Kubespawner's profile_list or ProfileSpawner to allow your
end users to choose the resources (memory, cpu, GPUs, etc) they want before
starting their server. Wouldn't it be nice if this information could be
embedded in the nbgitpuller link, so this (often confusing) choice is made
for your students?

While it would indeed be very nice, this is currently not easy for two
reasons:

1. nbgitpuller is a Jupyter Server extension, and only runs _after_ the server
   is started. It knows nothing about JupyterHub. So it can not influence the
   options JupyterHub uses to start the server.
2. There is UX complexity in what happens if the user clicks an nbgitpuller
   link when a server is _already_ running, but with a different set of resource
   requests / profile options. Do we shut that existing one down? Just error? Do
   nothing? Many valid options, but takes a bunch of work.

So while this workflow _is_ possible, it would most likely be done at the
JupyterHub level to make it possible, rather than in nbgitpuller

## Common errors

### Malformed links

Errors from clicking an nbgitpuller link usually stem from a malformed link, such as a mistake in the:

1. Source content repository link, such as pasting the wrong link into the **Git Repository URL** form field of the [](link.rst)
   - Wrong ❌ `https://github.com/owner/repo/tree/main/subpath`
   - Correct ✅ `https://github.com/owner/repo`
1. Providing the wrong or no branch name
   - Check that you have provided the correct branch name
   - Check that the git repository URL is correct

### Merge conflicts

Merge errors are usually mitigated by [](topic/automatic-merging.md), however unresolvable conflicts can occur if a link author force pushes changes to a repository, or a link consumer performs a merge commit. See Case 6 in [](topic/automatic-merging.md) for the `Backup and resync` solution for this particular merge error.

Consult the [](topic/repo-best-practices.md) for general advice on avoiding issues.
