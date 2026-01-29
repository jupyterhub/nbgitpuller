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

## Can I share content from a private repository?

```{warning}
Please do not include [personal access tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#about-personal-access-tokens) in the nbgitpuller link, e.g. using a GitHub repo URL of the form `https://login:<TOKEN>@hostname/path.git`, since this is logged on the Jupyter server. Anyone with access to the server can therefore see your private token.
```

If you would like to share content from a private GitHub repository, you can use [git-credential-helpers](https://github.com/yuvipanda/git-credential-helpers) to do so. This helper library lets git automatically create GitHub app installation tokens for interacting with private repos that have the GitHub app installed. Note that the steps below work for private GitHub repositories only.

### Steps

1. Install [git-credential-helpers](https://github.com/yuvipanda/git-credential-helpers) together with `nbgitpuller`
1. Setup a GitHub app to allow read access to the private repository
   - Create an app under your GitHub organization

   - Give it a descriptive name (such as 'nbgitpuller private repo access') and description, as users will see this when installing this app to authorize access to the private repo

   - Disable webhooks (uncheck the 'Active' checkbox under 'Webhooks'). All other textboxes can be left empty.

   - Under 'Repository permissions', select 'Read' for 'Contents'.

   - Under 'Where can this GitHub App be installed?', select 'Any account'. This will enable users to push to their own user repositories or other organization repositories, rather than just the app owner organization repos.

   - Create the application with the 'Create GitHub app' button.

   - Note for later the numeric 'App ID' from the app info page you should be redirected to.

   - Create a new private key for authentication with the `Generate a private key` button. This should download a private key file, that you should keep secure and configure in the next step.

1. For this to work across multiple user accounts, update the _system_ (not your local) `gitconfig` file with the following

   ```bash
   [credential "https://github.com"]
   helper = !git-credential-github-app --app-key-file <path-to-your-app-rsa-key-file> --app-id <id-of-your-github-app>
   useHttpPath = true
   ```

   ```{note}
   You must use the **private key**, not a **client secret**.
   ```

   - To configure helm chart values for [Zero to JupyterHub](https://z2jh.jupyter.org/en/stable/) clusters with the `gitconfig` file, see the documentation on [singleuser extra files](https://z2jh.jupyter.org/en/latest/resources/reference.html#singleuser-extrafiles)
      - We recommend setting `mountPath: /etc/gitconfig` and `stringData` with the contents of the `gitconfig` file above
      - However if the software image is using git from conda-forge, the file should be mounted in `${CONDA_PREFIX}/etc/gitconfig`
      - You can also try using `git config --system --list --show-origin` in the software image to show where the system-wide git config file is located.

1. Install the GitHub app to the private repo
   - Go to the ‘Public page’ of the GitHub app created. This usually is of the form `https://github.com/apps/<name-of-app>`. You can find this in the information page of the app after you create it, under ‘Public link’

   - Install the app into the account or the organization the private repo lives in, and grant it access only to the repo that needs to be pulled.
