// Pure function that generates an nbgitpuller URL
function generateRegularUrl(hubUrl, urlPath, repoUrl, branch, compressed, contentProvider) {

    // assume hubUrl is a valid URL
    var url = new URL(hubUrl);

    url.searchParams.set('repo', repoUrl);
    if(compressed) {
        url.searchParams.set('content_provider', contentProvider);
    }
    if (urlPath) {
        url.searchParams.set('urlpath', urlPath);
    }

    if (branch) {
        url.searchParams.set('branch', branch);
    } else if(contentProvider == "git"){
        url.searchParams.set('branch', "main");
    }

    if (!url.pathname.endsWith('/')) {
        url.pathname += '/'
    }
    url.pathname += 'hub/user-redirect/git-pull';

    return url.toString();
}

function generateCanvasUrl(hubUrl, urlPath, repoUrl, branch, compressed, contentProvider) {
    // assume hubUrl is a valid URL
    var url = new URL(hubUrl);

    var nextUrlParams = new URLSearchParams();

    nextUrlParams.append('repo', repoUrl);
    if(compressed) {
        nextUrlParams.append('content_provider', contentProvider);
    }
    if (urlPath) {
        nextUrlParams.append('urlpath', urlPath);
    }

    if (branch) {
        nextUrlParams.append('branch', branch);
    } else if(contentProvider == "git"){
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

function generateBinderUrl(hubUrl, userName, envRepoName, envGitBranch, urlPath,
    contentGitRepoUrl, contentGitRepoBranch, compressed, contentProvider) {

    var url = new URL(hubUrl);

    var nextUrlParams = new URLSearchParams();

    nextUrlParams.append('repo', contentGitRepoUrl);

    if(compressed) {
        nextUrlParams.append('content_provider', contentProvider);
    }
    if (urlPath) {
        nextUrlParams.append('urlpath', urlPath);
    }

    if (contentGitRepoBranch) {
        nextUrlParams.append('branch', contentGitRepoBranch);
    } else if(contentProvider == "git"){
        nextUrlParams.append('branch', "main");
    }

    if(envGitBranch == ""){
        envGitBranch = "main"
    }
    var nextUrl = 'git-pull?' + nextUrlParams.toString();

    var path = '/v2/gh/';
    url.pathname = path.concat(userName, "/", envRepoName, "/", envGitBranch);
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
    displayContentProvider();
}

/**
 * Return name of directory git will clone given repo to.
 *
 * nbgitpuller needs to redirect users to *inside* the directory it
 * just cloned. We copy the logic git itself uses to determine that.
 * See https://github.com/git/git/blob/1c52ecf4ba0f4f7af72775695fee653f50737c71/builtin/clone.c#L276
 *
 * The condition on the first line of this function ensures the user has not included a forward slash at the end of
 * the URL. If they do, it is removed so that the rest of the function can split by forward slash and parse the name
 * of directory from the URL.
 *
 * @param {string} gitCloneUrl This is the url to the git repo
 */
function generateCloneDirectoryName(gitCloneUrl) {
    if(gitCloneUrl.slice(-1) == "/")
        gitCloneUrl = gitCloneUrl.slice(0,-1);
    var lastPart = gitCloneUrl.split('/').slice(-1)[0];
    return lastPart.split(':').slice(-1)[0].replace(/(\.git|\.bundle)?/, '');
}

/**
 * This takes the values from the UI for content providers and sets three values in a
 * json object(contentProviderUrl, branch, and compressed) based on what contentProvider is selected in the UI.
 *
 * The args contains the contentProvider selected in the UI as well as whatever text(if any)
 * is in each of the content provider URL(e.g. driveURL, dropURL) text boxes, as well as the contentGitBranch.
 *
 * The return value is a a json object containing the branch, which may be an empty string if git is not the content
 * provider, the contentProviderURL, and a boolean key, compressed, that indicates if you our notebooks are in a
 * compressed archive.
 *
 * @param {json} args - contains UI element values for content providers(url, git branch,
 */
function configureContentProviderAttrs(args){
  contentProvider = args["contentProvider"];
  branch = "";
  compressed = true;
  contentProviderURL ="";
  if(contentProvider == "git"){
      contentProviderURL = args["contentGitRepoUrl"];
      branch = args["contentGitRepoBranch"];
      compressed = false;
  } else if(contentProvider == "googledrive"){
      contentProviderURL = args["driveUrl"];
  } else if(contentProvider == "dropbox"){
      contentProviderURL =  args["dropUrl"];
  } else if(contentProvider == "generic_web"){
      contentProviderURL =  args["webUrl"];
  }
  return {
      "branch": branch,
      "contentProviderURL": contentProviderURL,
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
        var webUrl = document.getElementById('generic-web-url').value;
        var envGitRepoUrl = document.getElementById('env-repo').value;
        var envGitBranch = document.getElementById('env-branch').value;
        var contentGitRepoUrl = document.getElementById('content-repo').value;
        var contentGitRepoBranch = document.getElementById('content-branch').value;
        var filePath = document.getElementById('filepath').value;
        var appName = form.querySelector('input[name="app"]:checked').value;
        var activeTab = document.querySelector(".nav-link.active").id;
        var contentProvider = form.querySelector('input[name="content-provider"]:checked').value;
        
        if (appName === 'custom') {
            var urlPath = document.getElementById('urlpath').value;
        } else {
            var envGitRepoName = generateCloneDirectoryName(envGitRepoUrl);
            var contentGitRepoName = generateCloneDirectoryName(contentGitRepoUrl);
            var partialUrlPath = contentGitRepoName + '/' + filePath;
            if(contentProvider !== "git"){
                contentGitRepoName = "";
                partialUrlPath = filePath;
            }
            var urlPath = apps[appName].generateUrlPath(partialUrlPath);
        }
        args = {
            "contentProvider": contentProvider,
            "contentGitRepoUrl": contentGitRepoUrl,
            "contentGitRepoBranch": contentGitRepoBranch,
            "driveUrl": driveUrl,
            "dropUrl": dropUrl,
            "webUrl": webUrl
        }
        config = configureContentProviderAttrs(args)
        if (activeTab === "tab-auth-default") {
            document.getElementById('default-link').value = generateRegularUrl(
                hubUrl, urlPath, config["contentProviderURL"], config["branch"], config["compressed"], contentProvider
            );
        } else if (activeTab === "tab-auth-canvas"){
            document.getElementById('canvas-link').value = generateCanvasUrl(
                hubUrl, urlPath, config["contentProviderURL"], config["branch"], config["compressed"], contentProvider
            );
        } else if (activeTab === "tab-auth-binder"){
            // FIXME: userName parsing using new URL(...) assumes a 
            // HTTP based repoUrl. Does it make sense to create a
            // BinderHub link for SSH URLs? Then let's fix this parsing.
            var userName = new URL(envGitRepoUrl).pathname.split('/')[1];
            document.getElementById('binder-link').value = generateBinderUrl(
                hubUrl, userName, envGitRepoName, envGitBranch, urlPath, config["contentProviderURL"], config["branch"], config["compressed"], contentProvider
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
/**
 * Depending on the content provider selected this hides and shows the appropriate divs
 *
 */
function displayContentProvider(){
    var form = document.getElementById('linkgenerator');
    var contentProvider = form.querySelector('input[name="content-provider"]:checked').value;
    hideShowByClassName(".content-provider", 'none');

    if(contentProvider == 'git'){
        hideShowByClassName(".content-provider-git", '');
    } else if(contentProvider == 'googledrive'){
        hideShowByClassName(".content-provider-googledrive", '');
    } else if(contentProvider == 'dropbox'){
        hideShowByClassName(".content-provider-dropbox", '');
    } else if(contentProvider =="generic_web"){
        hideShowByClassName(".content-provider-generic-web", '');
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
    document.querySelectorAll('#linkgenerator input[name="content-provider"]').forEach(
        function (element) {
            element.addEventListener('change', function(){
                displayContentProvider();
                render();
            });
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
    displayContentProvider();
    render();
}

window.onload = main;
