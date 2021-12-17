# Using `nbgitpuller`

## Overview of `nbgitpuller` links

`nbgitpuller`links may be sent to your users via any method you like - websites, emails, a learning management system, etc.
This link will contain at least the following information:

1. The location of the JupyterHub you are sending them to.
2. The git repository where you have published your content.
3. Optionally, a particular file or directory you want to automatically
4. Optionally, which UI should be opened when the user clicks the link.
   By default `nbgitpuller` uses the classic notebook interface - but you may instead use
   [JupyterLab](https://github.com/jupyterlab/jupyterlab/), [RStudio](https://github.com/jupyterhub/jupyter-rsession-proxy/), [Linux Desktop](https://github.com/jupyterhub/jupyter-remote-desktop-proxy), etc based on what you have available in your JupyterHub.
   open for your students once the repository has been synchronized. Note the entire repository will be copied, not just the specified file.

The first time a particular student clicks the link, a local copy of the
repository is made for the student. On successive clicks, the latest version
of the remote repository is fetched, and merged automatically with the
student's local copy using a {ref}`series of rules <topic/automatic-merging>`
that ensure students never get merge conflicts nor lose any of their changes.
## Create an `nbgitpuller` link via a web extension

The easiest way to create an `nbgitpuller` link is via a web extension  ([github repo](https://github.com/yuvipanda/nbgitpuller-link-generator-webextension)).
This allows you to quickly generate an `nbgitpuller` link directly from the content in your repository (e.g., on GitHub).
See the links below to download the extension.

- [Chrome extension](https://chrome.google.com/webstore/detail/nbgitpuller-link-generato/hpdbdpklpmppnoibabdkkhnfhkkehgnc)
- [Firefox extension](https://addons.mozilla.org/en-US/firefox/addon/nbgitpuller-link-generator/?utm_source=addons.mozilla.org&utm_medium=referral&utm_content=search)

## Automatically create an `nbgitpuller` link via a web app

You can also create an `nbgitpuller` link via a GUI web app at the below link:

[nbgitpuller.link](http://nbgitpuller.link)

This contains a simple web form where you paste the location of the content you'd like your users to pull, and it will generate a link for you to distribute.

## Manually create an `nbgitpuller` link


There is a short video showing 

```{raw} html
<iframe
     width="560" height="315"
     src="https://www.youtube-nocookie.com/embed/o7U0ZuICVFg"
     frameborder="0"
     allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture"
     allowfullscreen>
</iframe>
```

If you are interested in the details of available options when creating
the link, we have a {ref}`list of options <topic/url-options>` as well.