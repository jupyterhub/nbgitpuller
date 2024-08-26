# nbgitpuller

`nbgitpuller` lets you distribute content to a Jupyter user via the click of a button!
This allows your users to focus on the content without needing to understand `git`
or other version control machinery.

`nbgitpuller` provides {ref}`automatic, opinioned conflict resolution <topic/automatic-merging>`
by using `git` under the hood.
It is commonly used to distribute content to multiple users of a JupyterHub, though it works just fine on an individual person's computer, if they have Jupyter installed.

Here's an example of `nbgitpuller` in action:

1. The [nbgitpuller link generator](link) is used to create a link.

   ```{image} _static/nbgitpuller-link-generator.png

   ```

2. A user clicks the link, and the content is pulled into a live Jupyter session.

   ```{image} _static/nbgitpuller-demo.gif

   ```

## Use `nbgitpuller`

See [](use.md) for information about how to use `nbgitpuller`.
Here's a short overview:

1. Ensure your user has `nbgitpuller` installed. This is commonly done by installing it for all users of a JupyterHub. See [the installation instructions](install.rst) for more information.
2. Create an "`nbgitpuller` link" which points to the content you'd like to distribute (e.g., a Jupyter Notebook in a GitHub repository).
3. Tell your user to click the link, and `nbgitpuller` will automatically pull in the content to their file system.

### Generate an nbgitpuller link

There are several ways to generate an `nbgitpuller` link.
The two easiest ways to do so are:

- Via a browser extension to generate links directly from your repository ([Chrome extension](https://chrome.google.com/webstore/detail/nbgitpuller-link-generato/hpdbdpklpmppnoibabdkkhnfhkkehgnc), [Firefox extension](https://addons.mozilla.org/en-US/firefox/addon/nbgitpuller-link-generator/?utm_source=addons.mozilla.org&utm_medium=referral&utm_content=search)
- Via a GUI web-app [at `nbgitpuller.link`](http://nbgitpuller.link)

Fore more information about generating nbgitpuller links, see [](use.md).

### When to use `nbgitpuller`

Use nbgitpuller when:

1. You want an easy way to distribute content (notebooks, markdown files, etc) to Jupyter users without requiring them to use `git`.
2. You have an alternative method for _collecting_ content from your users, as `nbgitpuller` does not "push", it only "pulls".

You should **not** use nbgitpuller when:

1. Users want to **push** to a `git` repository that has your content.
   In this case, you should instruct them to just use `git` directly,
   since the assumptions and design of nbgitpuller will surprise you in
   unexpected ways if you are pushing with git but pulling with nbgitpuller.
2. Users want to perform **manual git operations** locally.
   Mixing manual git operations + automatic nbgitpuller operations will
   cause unwelcome surprises.

## Full Contents

```{toctree}
:maxdepth: 2

install
use
contributing
topic/automatic-merging
topic/url-options
topic/repo-best-practices
faq
link
```
