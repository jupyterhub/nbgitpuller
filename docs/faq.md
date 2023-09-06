# Frequently asked questions

## Can I automatically tell JupyterHub what kind of server to start (node size, profile name, etc) as part of my nbgitpuller link?

You can use Kubespawner's profile_list or ProfileSpawner to allow your
end users to choose the resources (memory, cpu, GPUs, etc) they want before
starting their server. Wouldn't it be nice if this information could be
embedded in the nbgitpuller link, so this (often confusing) choice is made
for your students?

While it would indeed be very nice, this is not currently possible for two
reasons:

1. nbgitpuller is a Jupyter Server extension, and only runs _after_ the server
   is started. It knows nothing about JupyterHub. So it can not influence the
   options JupyterHub uses to start the server.
2. There is UX complexity in what happens if the user clicks an nbgitpuller
   link when a server is _already_ running, but with a different set of resource
   requests / profile options. Do we shut that existing one down? Just error? Do
   nothing? Many valid options, but takes a bunch of work.

So while this workflow _is_ possible, it would most likely require work in
JupyterHub to make it possible, rather than in nbgitpuller
