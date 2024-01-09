nbgitpuller link generator
==========================

Use the following form to create your own ``nbgitpuller`` links.

.. note::

   Consider using the `nbgitpuller link generator browser extension <https://github.com/yuvipanda/nbgitpuller-link-generator-webextension>`_
   instead! Available for `Firefox <https://addons.mozilla.org/en-US/firefox/addon/nbgitpuller-link-generator/>`_ and
   `Chrome <https://chrome.google.com/webstore/detail/nbgitpuller-link-generato/hpdbdpklpmppnoibabdkkhnfhkkehgnc>`_.


.. raw:: html

   <div class="container">
       <form id="linkgenerator" class="form needs-validation">

           <div class="form-group">

             <ul class="nav nav-tabs justify-content-end" role="tablist">
               <li class="nav-item" role="presentation">
                 <button class="nav-link active" id="tab-auth-default" data-bs-toggle="tab" data-bs-target="#auth-default" type="button" role="tab" aria-controls="auth-default"  aria-selected="true" onclick="changeTab(this)">
                   <small>JupyterHub</small>
                 </button>
               </li>
               <li class="nav-item" role="presentation">
                 <button class="nav-link" id="tab-auth-canvas" data-bs-target="#auth-canvas" data-bs-toggle="tab" type="button" role="tab" aria-controls="auth-canvas"
                 aria-selected="false" onclick="changeTab(this)">
                   <small>Launch from Canvas</small>
                 </button>
               </li>
               <li class="nav-item" role="presentation">
                 <button class="nav-link" id="tab-auth-binder" data-bs-toggle="tab" data-bs-target="#auth-binder" type="button" role="tab" aria-controls="auth-binder"
                 aria-selected="false" onclick="changeTab(this)">
                   <small>Binder</small>
                 </button>
               </li>
             </ul>

             <div class="tab-content">
               <div class="tab-pane fade show active" id="auth-default" role="tabpanel" aria-labelledby="tab-auth-default" tabindex="0">
                 <input type="text" readonly class="form-control form-control" id="default-link" name="auth-default-link" placeholder="Generated link appears here...">
               </div>
               <div class="tab-pane fade" id="auth-canvas" role="tabpanel" aria-labelledby="tab-auth-canvas"  tabindex="0">
                 <input type="text" readonly class="form-control form-control" id="canvas-link" name="auth-canvas-link" placeholder="Generated canvas 'external app' link appears here...">
               </div>
               <div class="tab-pane fade" id="auth-binder" role="tabpanel" aria-labelledby="tab-auth-binder"  tabindex="0">
                 <input type="text" readonly class="form-control form-control" id="binder-link" name="auth-binder-link" placeholder="Generated Binder link appears here...">
               </div>
             </div>
           </div>

           <div class="form-group row">
             <label for="hub" class="col-sm-2 col-form-label">JupyterHub URL</label>
             <div class="col-sm-10">
               <input class="form-control" type="url" name="hub" id="hub" placeholder="https://hub.example.com"
                 required pattern="https?://.+">
               <div class="invalid-feedback">
                 Must be a valid web URL
               </div>
               <small class="form-text text-muted" id="hub-help-text">
                 The JupyterHub to send users to.
                 <a href="https://github.com/jupyterhub/nbgitpuller">nbgitpuller</a> must be installed in this hub.
               </small>
             </div>
           </div>

           <div class="form-group row">
             <label for="repo" class="col-sm-2 col-form-label">Git Repository URL</label>
             <div class="col-sm-6">
               <input class="form-control" type="text" id="repo" placeholder="https://github.com/example/test"
                 oninput="displayLink()" required pattern="((git|https?)://.+|git@.+:.+)">
               <div class="invalid-feedback">
                 Must be a valid git URL
               </div>
               <small class="form-text text-muted" id="env-repo-help-text" hidden="true">
                 The environment repository must have
                 <a href="https://github.com/jupyterhub/nbgitpuller">nbgitpuller</a> installed.
               </small>
             </div>
             <div class="col-sm-4">
               <div class="input-group">
                 <div class="input-group-prepend">
                   <span class="input-group-text" id="branch-prepend-label">branch</span>
                 </div>
                 <input name="branch" id="branch" type="text" class="form-control" placeholder="default" aria-label="Branch Name" aria-describedby="branch-prepend-label">
                 <div class="invalid-feedback">
                    Must specify a branch name
                 </div>
               </div>
             </div>
           </div>

           <div class="form-group row" id="content-repo-group" hidden="true">
             <label for="content-repo" class="col-sm-2 col-form-label">Git Content Repository URL</label>
             <div class="col-sm-6">
               <input class="form-control" type="text" id="content-repo" placeholder="https://github.com/example/test"
                 oninput="displayLink()" pattern="((git|https?)://.+|git@.+:.+)">
               <div class="invalid-feedback">
                 Must be a valid git URL
               </div>
             </div>
             <div class="col-sm-4">
               <div class="input-group" id="content-branch-group" hidden="true">
                 <div class="input-group-prepend">
                   <span class="input-group-text" id="content-branch-prepend-label">branch</span>
                 </div>
                 <input name="content-branch" id="content-branch" type="text" class="form-control" value="master" aria-label="Branch Name" aria-describedby="content-branch-prepend-label">
               </div>
             </div>
            </div>

           <div class="form-group row" id="filepath-container">
             <label for="filepath" class="col-sm-2 col-form-label">File to open</label>
             <div class="col-sm-10">
               <input class="form-control" type="text" id="filepath" placeholder="index.ipynb"
                 oninput="displayLink()">
               <small class="form-text text-muted">
                 This file or directory from within the repo will open when user clicks the link.
               </small>
             </div>
           </div>

           <div class="form-group row" id="app-container">
             <div class="col-sm-2 col-form-label">
               <label for="app" class=>Application to Open</label>
               <small class="form-text text-muted">
               </small>
             </div>
             <div class="col-sm-10">
               <div class="form-check">
                 <input class="form-check-input" type="radio" name="app" id="app-classic" value="classic" checked>
                 <label class="form-check-label text-dark" for="app-classic">
                   Classic Jupyter Notebook
                 </label>
               </div>
               <div class="form-check">
                 <input class="form-check-input" type="radio" name="app" id="app-retrolab" value="retrolab">
                 <label class="form-check-label text-dark" for="app-retrolab">
                   RetroLab
                 </label>
               </div>
               <div class="form-check">
                 <input class="form-check-input" type="radio" name="app" id="app-jupyterlab" value="jupyterlab">
                 <label class="form-check-label text-dark" for="app-jupyterlab">
                   JupyterLab
                 </label>
               </div>
               <div class="form-check">
                 <input class="form-check-input" type="radio" name="app" id="app-rstudio" value="rstudio">
                 <label class="form-check-label text-dark" for="app-rstudio">
                   RStudio
                 </label>
               </div>
               <div class="form-check">
                 <input class="form-check-input" type="radio" name="app" id="app-shiny" value="shiny">
                 <label class="form-check-label text-dark" for="app-shiny">
                   Shiny
                 </label>
               </div>
               <div class="form-check">
                 <input class="form-check-input" type="radio" name="app" id="app-custom" value="custom">
                 <label class="form-check-label text-dark" for="app-custom">Custom URL</label>
                 <input class="form-control form-control-sm" type="text" id="urlpath" placeholder="Relative URL to redirect user to"
                   oninput="displayLink()">
               </div>
             </div>
           </div>

           <div class="form-group row" id="server-container">
            <label for="server" class="col-sm-2 col-form-label">Named Server to open</label>
            <div class="col-sm-10">
              <input class="form-control" type="text" id="server" placeholder="NamedServer"
                oninput="displayLink()">
              <small class="form-text text-muted">
                Use for specific <a href="https://jupyterhub.readthedocs.io/en/stable/howto/configuration/config-user-env.html#named-servers">named server</a> Jupyter server instance.
              </small>
            </div>
          </div>

       </form>
     </div>
     <br /><br /><br />

     <script type="text/javascript">
         // load link javascript on page load
         window.addEventListener("load", linkMain);
     </script>


**Pre-populating some fields in the link generator**

You can pre-populate some fields in order to make it easier for some
users to create their own links. To do so, use the following URL
parameters **when accessing this page**:

* ``hub`` is the URL of a JupyterHub
* ``repo`` is the URL of a GitHub repository to which you're linking
* ``branch`` is the branch you wish to pull from the Repository

For example, the following URL will pre-populate the form with the
UC Berkeley DataHub as the JupyterHub::

    https://nbgitpuller.readthedocs.io/link.html?hub=https://datahub.berkeley.edu


**Activating a tab when someone lands on this page**

You can also activate one of the tabs in the form above by default when a user lands
on this page. To do so, use the ``tab=`` query parameter. Here are the possible values:

* ``?tab=binder`` - activates the Binder tab
* ``?tab=canvas`` - activates the Canvas tab
