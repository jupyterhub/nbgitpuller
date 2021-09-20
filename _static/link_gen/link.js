// Pure function that generates an nbgitpuller URL
function generateRegularUrl(hubUrl, urlPath, repoUrl, branch, compressed, source) {

    // assume hubUrl is a valid URL
    var url = new URL(hubUrl);

    url.searchParams.set('repo', repoUrl);
    
    if(compressed) {
      url.searchParams.set('provider', source);
    }
    
    if (urlPath) {
        url.searchParams.set('urlpath', urlPath);
    }

    if (branch) {
        url.searchParams.set('branch', branch);
    } else if(source == "git"){
        url.searchParams.set('branch', "main");
    }
    
    if (!url.pathname.endsWith('/')) {
        url.pathname += '/'
    }
    url.pathname += 'hub/user-redirect/git-pull';

    return url.toString();
}

function generateCanvasUrl(hubUrl, urlPath, repoUrl, branch, compressed, source) {
    // assume hubUrl is a valid URL
    var url = new URL(hubUrl);

    var nextUrlParams = new URLSearchParams();

    nextUrlParams.append('repo', repoUrl);
    
    if(compressed) {
      nextUrlParams.append('provider', source);
    }
    
    if (urlPath) {
        nextUrlParams.append('urlpath', urlPath);
    }

    if (branch) {
        nextUrlParams.append('branch', branch);
    } else if(source == "git"){
        nextUrlParams.append('branch', "main");
    }

    var nextUrl = '/hub/user-redirect/git-pull?' + nextUrlParams.toString();

    if (!url.pathname.endsWith('/')) {
        url.pathname += '/'
    }
    url.pathname += 'hub/lti/launch'
    url.searchParams.append('next', nextUrl);

    return url.toString();
}

function generateBinderUrl(hubUrl, userName, repoName, branch, urlPath,
    contentRepoUrl, contentRepoBranch, compressed, source) {

    var url = new URL(hubUrl);

    var nextUrlParams = new URLSearchParams();

    nextUrlParams.append('repo', contentRepoUrl);

    if(compressed) {
      nextUrlParams.append('provider', source);
    }
    
    if (urlPath) {
        nextUrlParams.append('urlpath', urlPath);
    }

    if (contentRepoBranch) {
        nextUrlParams.append('branch', contentRepoBranch);
    } else if(source == "git"){
        nextUrlParams.append('branch', "main");
    }

    var nextUrl = 'git-pull?' + nextUrlParams.toString();

    var path = '/v2/gh/';
    url.pathname = path.concat(userName, "/", repoName, "/", branch);
    url.searchParams.append('urlpath', nextUrl);

    return url.toString();
}

var apps = {
    classic: {
        title: 'Classic Notebook',
        generateUrlPath: function (path) { return 'tree/' + path; },
    },
    jupyterlab: {
        title: 'JupyterLab',
        generateUrlPath: function (path) { return 'lab/tree/' + path; }
    },
    shiny: {
        title: 'Shiny',
        generateUrlPath: function (path) {
            // jupyter-shiny-proxy requires everything to end with a trailing slash
            if (!path.endsWith("/")) {
                path = path + "/";
            }
            return 'shiny/' + path;
        }
    },
    rstudio: {
        title: 'RStudio',
        generateUrlPath: function (path) { return 'rstudio/'; }
    }
}

function clearLinks(){
    document.getElementById('default-link').value = "";
    document.getElementById('binder-link').value = "";
    document.getElementById('canvas-link').value = "";
}


function changeTab(div) {
    var hub = document.getElementById("hub");
    var hub_help_text = document.getElementById("hub-help-text");
    var env_repo_group = document.getElementById("env-repo-group");
    var env_repo = document.getElementById("env-repo");
    var id = div.id;
    var form = document.getElementById('linkgenerator');
    
    clearLinks();
    if (id.includes("binder")) {
        hub.placeholder = "https://mybinder.org";
        hub.value = "https://mybinder.org";
        hub_help_text.hidden = true;
        hub.labels[0].innerHTML = "BinderHub URL";
        
        env_repo_group.style.display = '';
        env_repo.disabled = false;

    } else {
        hub.placeholder = "https://hub.example.com";
        hub.value = "";
        hub_help_text.hidden = false;
        hub.labels[0].innerHTML = "JupyterHub URL";
        
        env_repo_group.style.display = 'none';
        env_repo.disabled = true;
    }
    displaySource();
}

/**
 * Return name of directory git will clone given repo to.
 *
 * nbgitpuller needs to redirect users to *inside* the directory it
 * just cloned. We copy the logic git itself uses to determine that.
 * See https://github.com/git/git/blob/1c52ecf4ba0f4f7af72775695fee653f50737c71/builtin/clone.c#L276
 */
function generateCloneDirectoryName(gitCloneUrl) {
    if(gitCloneUrl.slice(-1) == "/")
      gitCloneUrl = gitCloneUrl.slice(0,-1);
    var lastPart = gitCloneUrl.split('/').slice(-1)[0];
    return lastPart.split(':').slice(-1)[0].replace(/(\.git|\.bundle)?/, '');
}

function handleSource(args){
  source = args["source"];
  branch = "";
  compressed = true;
  sourceUrl ="";
  if(source == "git"){
      sourceUrl = args["contentRepoUrl"];
      branch = args["contentRepoBranch"];
      compressed = false;
  } else if(source == "googledrive"){
      sourceUrl = args["driveUrl"];
  } else if(source == "dropbox"){
      sourceUrl =  args["dropUrl"];
  } else if(source == "standard"){
      sourceUrl =  args["webUrl"];
  }
  return {
    "branch": branch,
    "sourceUrl": sourceUrl,
    "compressed": compressed
  }
}

function displayLink() {
    var form = document.getElementById('linkgenerator');
    
    form.classList.add('was-validated');
    if (form.checkValidity()) {
        var hubUrl = document.getElementById('hub').value;
        var driveUrl = document.getElementById('drive-url').value;
        var dropUrl = document.getElementById('drop-url').value;
        var webUrl = document.getElementById('standard-url').value;
        var envRepoUrl = document.getElementById('env-repo').value;
        var envGitBranch = document.getElementById('env-branch').value;
        var contentRepoUrl = document.getElementById('content-repo').value;
        var contentRepoBranch = document.getElementById('content-branch').value;
        var filePath = document.getElementById('filepath').value;
        var appName = form.querySelector('input[name="app"]:checked').value;
        var activeTab = document.querySelector(".nav-link.active").id;
        var source = form.querySelector('input[name="source"]:checked').value;
        
        if (appName === 'custom') {
            var urlPath = document.getElementById('urlpath').value;
        } else {
            var repoName = generateCloneDirectoryName(contentRepoUrl);
            if(source !== "git"){
              repoName = ""
            }
            var urlPath;
            if (activeTab === "tab-auth-binder") {
                var contentRepoName = new URL(contentRepoUrl).pathname.split('/').pop().replace(/\.git$/, '');
                urlPath = apps[appName].generateUrlPath(contentRepoName + '/' + filePath);
            } else {
                urlPath = apps[appName].generateUrlPath(repoName + '/' + filePath);
            }
        }
        args = {
          "source": source,
          "contentRepoUrl": contentRepoUrl,
          "contentRepoBranch": contentRepoBranch,
          "driveUrl": driveUrl,
          "dropUrl": dropUrl,
          "webUrl": webUrl
        }
        config = handleSource(args)
        if (activeTab === "tab-auth-default") {
            document.getElementById('default-link').value = generateRegularUrl(
                hubUrl, urlPath, config["sourceUrl"], config["branch"], config["compressed"], source
            );
        } else if (activeTab === "tab-auth-canvas"){
            document.getElementById('canvas-link').value = generateCanvasUrl(
                hubUrl, urlPath, config["sourceUrl"], config["branch"], config["compressed"], source
            );
        } else if (activeTab === "tab-auth-binder"){
            // FIXME: userName parsing using new URL(...) assumes a 
            // HTTP based repoUrl. Does it make sense to create a
            // BinderHub link for SSH URLs? Then let's fix this parsing.
            var userName = new URL(envRepoUrl).pathname.split('/')[1];
            document.getElementById('binder-link').value = generateBinderUrl(
                hubUrl, userName, repoName, envGitBranch, urlPath, config["sourceUrl"], config["branch"], config["compressed"], source
            );
        }
    } else {
        clearLinks();
    }
}

function populateFromQueryString() {
    // preseed values if specified in the url
    var params = new URLSearchParams(window.location.search);
    // Parameters are read from query string, and <input> fields are set to them
    var allowedParams = ['hub', 'repo', 'content-repo', 'branch', 'app', 'urlpath'];
    if (params.has("urlpath")) {
        // setting urlpath implies a custom app
        document.getElementById('app-custom').checked = true;
    }
    for (var i = 0; i < allowedParams.length; i++) {
        var param = allowedParams[i];
        if (params.has(param)) {
            if ((param === 'app') && !params.has("urlpath")) {
                radioId = 'app-' + params.get(param).toLowerCase();
                document.getElementById(radioId).checked = true;
            } else {
                document.getElementById(param).value = params.get(param);
            }
        }
    }
}

function hideShowByClassName(cls, hideShow){
  [].forEach.call(document.querySelectorAll(cls), function (el) {
    el.style.display = hideShow;
    setDisabled = (hideShow == 'none')
    $(el).find("input").each(function(){
        $(this).prop("disabled", setDisabled);
    });
  });
}


function displaySource(){
    var form = document.getElementById('linkgenerator');
    var source = form.querySelector('input[name="source"]:checked').value;
    hideShowByClassName(".source", 'none');

    if(source == 'git'){
        hideShowByClassName(".source-git", '');
    } else if(source == 'googledrive'){
        hideShowByClassName(".source-googledrive", '');
    } else if(source == 'dropbox'){
        hideShowByClassName(".source-dropbox", '');
    } else if(source =="standard"){
        hideShowByClassName(".source-standard", '');
    }
}

/**
 * Main loop of the program.
 *
 * Called whenever any state changes (input received, page loaded, etc).
 * Should turn on / off elements based only on current state, and display the link
 *
 * Sort of react-ish.
 */
function render() {
    var form = document.getElementById('linkgenerator');
    var appName = form.querySelector('input[name="app"]:checked').value;

    
    if (appName == 'custom') {
        document.getElementById('urlpath').disabled = false;
        document.getElementById('filepath').disabled = true;
    } else {
        document.getElementById('urlpath').disabled = true;

        var app = apps[appName];
        if (!app.generateUrlPath) {
            document.getElementById('filepath').disabled = true;
        } else {
            document.getElementById('filepath').disabled = false;
        }
    }

    displayLink();
}

/**
 * Entry point
 */
function main() {
    // Hook up any changes in form elements to call render()
    document.querySelectorAll('#linkgenerator input[name="app"]').forEach(
        function (element) {
            element.addEventListener('change', render);
        }
    )
    document.querySelectorAll('#linkgenerator input[name="source"]').forEach(
        function (element) {
            element.addEventListener('change', function(){
                displaySource();
                render();
              }
            );
        }
    )
    
    document.querySelectorAll('#linkgenerator input[type="text"], #linkgenerator input[type="url"]').forEach(
        function (element) {
            element.addEventListener('input', render);
        }
    )

    populateFromQueryString();

    // Activate tabs based on search parameters
    var params = new URL(window.location).searchParams;
    if (params.get("tab")) {
      if (params.get("tab") === "binder") {
        $("#tab-auth-binder").click()
      } else if (params.get("tab") === "canvas") {
        $("#tab-auth-canvas").click()
      }
    }

    
    // Do an initial render, to make sure our disabled / enabled properties are correctly set
    displaySource();
    render();
}

window.onload = main;
