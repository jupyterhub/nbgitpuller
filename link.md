<!--
  nbgitpuller link generator

  Required inputs: a JupyterHub url and a git repository.
  Optional inputs: a hub path and a git branch.

  We validate the hub url so that we can reliably accept, manipulate, and
  display urls. We do not validate the repo url since nbgitpuller
  doesn't, but we could.
--!>

   <link rel="stylesheet" href="https://unpkg.com/purecss@1.0.0/build/pure-min.css" integrity="sha384-nn4HPE8lTHyVtfCBi5yW9d20FjT8BJwUXyWZT9InLYax14RDjBj46LmSztkmNP9w" crossorigin="anonymous">

   <style>
   input[type=button] {
    font-size: 1rem;
    line-height: 1.5;
    background-color: #477dca;
    border-radius: 3px;
    border: none;
    color: white;
    display: inline-block;
    font-weight: 700;
    padding: 6px 18px;
    margin-top: 1em;
    text-decoration: none
   }
   #error {
     color: red;
   }

   /* https://www.the-art-of-web.com/html/html5-form-validation/ */
   input:invalid {
     background-image: url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAeVJREFUeNqkU01oE1EQ/mazSTdRmqSxLVSJVKU9RYoHD8WfHr16kh5EFA8eSy6hXrwUPBSKZ6E9V1CU4tGf0DZWDEQrGkhprRDbCvlpavan3ezu+LLSUnADLZnHwHvzmJlvvpkhZkY7IqFNaTuAfPhhP/8Uo87SGSaDsP27hgYM/lUpy6lHdqsAtM+BPfvqKp3ufYKwcgmWCug6oKmrrG3PoaqngWjdd/922hOBs5C/jJA6x7AiUt8VYVUAVQXXShfIqCYRMZO8/N1N+B8H1sOUwivpSUSVCJ2MAjtVwBAIdv+AQkHQqbOgc+fBvorjyQENDcch16/BtkQdAlC4E6jrYHGgGU18Io3gmhzJuwub6/fQJYNi/YBpCifhbDaAPXFvCBVxXbvfbNGFeN8DkjogWAd8DljV3KRutcEAeHMN/HXZ4p9bhncJHCyhNx52R0Kv/XNuQvYBnM+CP7xddXL5KaJw0TMAF8qjnMvegeK/SLHubhpKDKIrJDlvXoMX3y9xcSMZyBQ+tpyk5hzsa2Ns7LGdfWdbL6fZvHn92d7dgROH/730YBLtiZmEdGPkFnhX4kxmjVe2xgPfCtrRd6GHRtEh9zsL8xVe+pwSzj+OtwvletZZ/wLeKD71L+ZeHHWZ/gowABkp7AwwnEjFAAAAAElFTkSuQmCC);
     background-position: right top;
     background-repeat: no-repeat;
   }
   input:required:valid {
      background-image: url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAepJREFUeNrEk79PFEEUx9/uDDd7v/AAQQnEQokmJCRGwc7/QeM/YGVxsZJQYI/EhCChICYmUJigNBSGzobQaI5SaYRw6imne0d2D/bYmZ3dGd+YQKEHYiyc5GUyb3Y+77vfeWNpreFfhvXfAWAAJtbKi7dff1rWK9vPHx3mThP2Iaipk5EzTg8Qmru38H7izmkFHAF4WH1R52654PR0Oamzj2dKxYt/Bbg1OPZuY3d9aU82VGem/5LtnJscLxWzfzRxaWNqWJP0XUadIbSzu5DuvUJpzq7sfYBKsP1GJeLB+PWpt8cCXm4+2+zLXx4guKiLXWA2Nc5ChOuacMEPv20FkT+dIawyenVi5VcAbcigWzXLeNiDRCdwId0LFm5IUMBIBgrp8wOEsFlfeCGm23/zoBZWn9a4C314A1nCoM1OAVccuGyCkPs/P+pIdVIOkG9pIh6YlyqCrwhRKD3GygK9PUBImIQQxRi4b2O+JcCLg8+e8NZiLVEygwCrWpYF0jQJziYU/ho2TUuCPTn8hHcQNuZy1/94sAMOzQHDeqaij7Cd8Dt8CatGhX3iWxgtFW/m29pnUjR7TSQcRCIAVW1FSr6KAVYdi+5Pj8yunviYHq7f72po3Y9dbi7CxzDO1+duzCXH9cEPAQYAhJELY/AqBtwAAAAASUVORK5CYII=);
     background-position: right top;
     background-repeat: no-repeat;
   }
   </style>

   <h1>nbgitpuller link generator</h1>

   <form id="linkgenerator" class="pure-form pure-form-aligned">
     <fieldset>
       <div class="pure-control-group">
         <label for="hub">JupyterHub URL</label>
         <input class="pure-input-2-3" type="url" name="hub" id="hub" placeholder="https://example.com" required pattern="https?://.+">
         <span id="error" class="pure-form-message-inline"></span>
       </div>
       <div class="pure-control-group">
         <label for="urlpath">URL path</label>
         <input class="pure-input-1-3" type="text" id="urlpath" placeholder="urlpath">
         <span class="pure-form-message-inline">(e.g. "lab", "rstudio", "notebooks/materials-fa18/materials/fa18/lab/lab01/lab01.ipynb")</span>
       </div>
     </fieldset>
     <fieldset>
       <div class="pure-control-group">
         <label for="repo">Repository URL</label>
         <input class="pure-input-2-3" type="text" id="repo" placeholder="https://github.com/example/test" required>
       </div>
       <div class="pure-control-group">
         <label for="repo">Git Branch</label>
         <input class="pure-input-1-3" type="text" id="branch" placeholder="branch">
       </div>
       <div class="pure-control-group">
         <input type="button" id="generatebutton" onclick="generateLink()" value="Generate Link" >
         <input type="button" id="resetbutton" onclick="resetForm()" value="Reset" >
       </div>
     </fieldset>
   </form>

   <hr />

   <div><a id="link" href=""></a></div>

   <script>
     /* preseed read-only values if specified on the url */
     var urlparams = new URLSearchParams(window.location.search);
     var i, val, input, elements = ['hub', 'repo', 'branch', 'urlpath'];
     for (i=0; i < elements.length; i++) {
       if (!urlparams.has(elements[i])) continue;
       val = urlparams.get(elements[i]);
       input = document.getElementById(elements[i]);
       input.value = val;
       input.readOnly = true;
     }
   </script>

   <script>
   /* generate and display the link */
   function generateLink() {
       var hub   = document.getElementById("hub").value;
       var error = document.getElementById('error')
       try {
         var huburl = new URL(hub);
       } catch(err) {
         error.innerHTML = "invalid url";
         return;
       }
       error.innerHTML = "";
       var query  = huburl.searchParams;

       var val, elements = ['repo', 'branch', 'urlpath'];
       for (var i=0; i < elements.length; i++) {
         val = document.getElementById(elements[i]).value;
         if (val.length == 0) continue;
         query.set(elements[i], val)
       }

       huburl.pathname += 'hub/user-redirect/git-pull';

       var newurl = huburl.toString();

       var a = document.getElementById('link')
       a.setAttribute('id', "link");
       a.setAttribute('href', newurl);
       a.innerHTML = newurl;

       console.log(newurl);
   }

   /* blank all input fields and remove the read-only attributes. we don't
    * invoke reset on the form itself since we have to loop over the
    * elements anyways to make them read/write */
   function resetForm() {
     var i, input, elements = ['hub', 'repo', 'branch', 'urlpath'];
     for (i=0; i < elements.length; i++) {
       input = document.getElementById(elements[i]);
       input.value = "";
       input.readOnly = false;
     }
     document.getElementById('error').innerHTML = "";
   }
   </script>
