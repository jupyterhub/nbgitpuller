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
Please do not include [personal access tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#about-personal-access-tokens) in the nbgitpuller link, e.g. using a GitHub repo URL of the form `https://login:<TOKEN>@hostname/path.git`, since this is logged on the Jupyter server. Anyone with access to server can therefore see your private token.
```

If you would like to share content from a private repository, you can use [git-credential-helpers](https://github.com/yuvipanda/git-credential-helpers) to do so.

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

1. Update `gitconfig` file with the following

   ```bash
   [credential "https://github.com"]
   helper = !git-credential-github-app --app-key-file <path-to-your-app-rsa-key-file> --app-id <id-of-your-github-app>
   useHttpPath = true
   ```

   ```{note}
   You must use the **private key**, not a **client secret**.
   ```

   - To configure helm chart values for [Zero to JupyterHub](https://z2jh.jupyter.org/en/stable/) clusters, see [this example](https://infrastructure.2i2c.org/howto/features/private-nbgitpuller/#helm-values-configuration).

1. Install the GitHub app to the private repo
   - Go to the ‘Public page’ of the GitHub app created. This usually is of the form `https://github.com/apps/<name-of-app>`. You can find this in the information page of the app after you create it, under ‘Public link’

   - Install the app into the account or the organization the private repo lives in, and grant it access only to the repo that needs to be pulled.
