# Generate an nbgitpuller link for your JupyterHub

   <link rel="stylesheet" href="https://unpkg.com/purecss@1.0.0/build/pure-min.css" integrity="sha384-nn4HPE8lTHyVtfCBi5yW9d20FjT8BJwUXyWZT9InLYax14RDjBj46LmSztkmNP9w" crossorigin="anonymous">

   <style>
   input#generatebutton {
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
   </style>

   <form id="linkgenerator" class="pure-form">
      <input type="text" class="pure-input-1-4" id="hub" placeholder="hub url">
      <input type="text" class="pure-input-1-4" id="repo" placeholder="repo url">
      <input type="text" class="pure-input-1-4" id="branch" placeholder="branch">
      <input type="text" class="pure-input-1-4" id="subPath" placeholder="filepath">
      <input type="text" class="pure-input-1-4" id="app" placeholder="app">
      <input type="button" id="generatebutton" onclick="generateLink()" value="Generate Link" />
   </form>

   <hr />

   <div><a id="link" href=""></a></div>

   <script>
   function generateLink() {
       var hub    = document.getElementById("hub").value;
       var huburl = new URL(hub);
       var query  = huburl.searchParams;

       var elements = ['repo', 'branch', 'subPath', 'app'];
       var val;
       for (var i=0; i < elements.length; i++) {
         val = document.getElementById(elements[i]).value;
         if (val.length == 0) continue;
         // TODO: sanitize
         query.set(elements[i], val)
       }

       huburl.pathname += 'hub/user-redirect/git-pull';

       var newurl = huburl.toString();
       /*newurl = encodeURI(newurl);*/

       var a = document.getElementById('link')
       a.setAttribute('id', "link");
       a.setAttribute('href', newurl);
       a.innerHTML = newurl;
   }
   </script>
