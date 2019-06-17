nbgitpuller link generator
==========================

Use the following form to create your own ``nbgitpuller`` links.

.. raw:: html

   <div class="container">     
       <form id="linkgenerator" class="form needs-validation" onchange="onFormChange">
   
           <div class="form-group">
   
             <ul class="nav nav-tabs justify-content-end" role="tablist">
               <li class="nav-item">
                 <a class="nav-link active" id="tab-auth-default" data-toggle="tab" role="tab" href="#auth-default" aria-controls="auth-default">
                   <small>Default</small>
                 </a>
               </li>
               <li class="nav-item">
                 <a class="nav-link" id="tab-auth-canvas" data-toggle="tab" role="tab" href="#auth-canvas" aria-controls="auth-canvas">
                   <small>Launch from Canvas</small>
                 </a>
               </li>
             </ul>
   
             <div class="tab-content">
               <div class="tab-pane fade show active" id="auth-default" role="tabpanel" aria-labelledby="tab-auth-default">
                 <input type="text" readonly class="form-control form-control" id="default-link" name="auth-default-link" placeholder="Generated link appears here...">
               </div>
               <div class="tab-pane fade" id="auth-canvas" role="tabpanel" aria-labelledby="tab-auth-canvas">
                 <input type="text" readonly class="form-control form-control" id="canvas-link" name="auth-canvas-link" placeholder="Generated canvas 'external app' link appears here...">
               </div>
             </div>
             </ul>
           </div>
   
           <div class="form-group row">
             <label for="hub" class="col-sm-2 col-form-label">JupyterHub URL</label>
             <div class="col-sm-10">
               <input class="form-control" type="url" name="hub" id="hub" placeholder="https://hub.example.com"
                 required pattern="https?://.+">
               <div class="invalid-feedback">
                 Must be a valid web URL
               </div>
               <small class="form-text text-muted">
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
             </div>
             <div class="col-sm-4">
               <div class="input-group">
                 <div class="input-group-prepend">
                   <span class="input-group-text" id="branch-prepend-label">branch</span>
                 </div>
                 <input name="branch" id="branch" type="text" class="form-control" placeholder="master" aria-label="Branch Name" aria-describedby="branch-prepend-label">
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
                 <input class="form-check-input" type="radio" name="app" id="app-custom" value="custom">
                 <label class="form-check-label text-dark" for="app-custom">Custom URL</label>
                 <input class="form-control form-control-sm" type="text" id="urlpath" placeholder="Relative URL to redirect user to"
                   oninput="displayLink()">
               </div>
             </div>
           </div>
   
       </form>
     </div>
     <br /><br /><br />


**Pre-populating some fields in the link generator**

You can pre-populate some fields in order to make it easier for some
users to create their own links. To do so, use the following URL
parameters **when accessing this page**:

* ``hub`` is the URL of a JupyterHub
* ``repo`` is the URL of a github repository to which you're linking
* ``branch`` is the branch you wish to pull from the Repository

For example, the following URL will pre-populate the form with the
UC Berkeley DataHub as the JupyterHub::

    https://jupyterhub.github.io/nbgitpuller/link?hub=https://datahub.berkeley.edu