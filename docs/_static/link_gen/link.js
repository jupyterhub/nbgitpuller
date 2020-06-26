// Pure function that generates an nbgitpuller URL
function generateRegularUrl(hubUrl, urlPath, repoUrl, branch) {

    // assume hubUrl is a valid URL
    var url = new URL(hubUrl);

    url.searchParams.set('repo', repoUrl);

    if (urlPath) {
        url.searchParams.set('urlpath', urlPath);
    }

    if (branch) {
        url.searchParams.set('branch', branch);
    }

    url.pathname += 'hub/user-redirect/git-pull';

    return url.toString();
}

function generateCanvasUrl(hubUrl, urlPath, repoUrl, branch) {
    // assume hubUrl is a valid URL
    var url = new URL(hubUrl);

    var nextUrlParams = new URLSearchParams();

    nextUrlParams.append('repo', repoUrl);

    if (urlPath) {
        nextUrlParams.append('urlpath', urlPath);
    }

    if (branch) {
        nextUrlParams.append('branch', branch);
    }

    var nextUrl = '/hub/user-redirect/git-pull?' + nextUrlParams.toString();

    url.pathname = '/hub/lti/launch'
    url.searchParams.append('next', nextUrl);

    return url.toString();
}

function generateMyBinderUrl(hubUrl, userName, repoName, branch, urlPath,
    contentRepoUrl, contentRepoBranch) {

    var url = new URL(hubUrl);

    var nextUrlParams = new URLSearchParams();

    nextUrlParams.append('repo', contentRepoUrl);

    if (urlPath) {
        nextUrlParams.append('urlpath', urlPath);
    }

    if (branch) {
        nextUrlParams.append('branch', branch);
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
    rstudio: {
        title: 'RStudio',
        generateUrlPath: function (path) { return 'rstudio/'; }
    }
}

function changeTab(div) {
    var hub = document.getElementById("hub");
    var env_repo = document.getElementById("repo");
    var content_repo = document.getElementById("content-repo");
    var content_branch = document.getElementById("content-branch");
    var id = div.id;

    if (id.includes("mybinder")) {
        hub.placeholder = "https://mybinder.org";
        env_repo.labels[0].innerHTML = "Git Environment Repository URL";
        content_repo.disabled = false;
        content_branch.disabled = false;
    } else {
        hub.placeholder = "https://hub.example.com";
        hub.disabled = false;
        env_repo.labels[0].innerHTML = "Git Repository URL";
        content_repo.disabled = true;
        content_branch.disabled = true;
    }
}

function displayLink() {
    var form = document.getElementById('linkgenerator');

    form.classList.add('was-validated');
    if (form.checkValidity()) {
        var hubUrl = document.getElementById('hub').value;
        var repoUrl = document.getElementById('repo').value;
        var branch = document.getElementById('branch').value;
        var contentRepoUrl = document.getElementById('content-repo').value;
        var contentRepoBranch = document.getElementById('content-branch').value;
        var filePath = document.getElementById('filepath').value;
        var appName = form.querySelector('input[name="app"]:checked').value;

        if (appName === 'custom') {
            var urlPath = document.getElementById('urlpath').value;
        } else {
            var repoName = new URL(repoUrl).pathname.split('/').pop().replace(/\.git$/, '');
            var userName = new URL(repoUrl).pathname.split('/')[1];
            var urlPath;
            if (contentRepoUrl.disabled) {
                urlPath = apps[appName].generateUrlPath(repoName + '/' + filePath);
            } else {
                var contentRepoName = new URL(contentRepoUrl).pathname.split('/').pop().replace(/\.git$/, '');
                urlPath = apps[appName].generateUrlPath(contentRepoName + '/' + filePath);
            }
        }

        document.getElementById('default-link').value = generateRegularUrl(
            hubUrl, urlPath, repoUrl, branch
        );
        document.getElementById('canvas-link').value = generateCanvasUrl(
            hubUrl, urlPath, repoUrl, branch
        );
        document.getElementById('mybinder-link').value = generateMyBinderUrl(
            hubUrl, userName, repoName, branch, urlPath, contentRepoUrl, contentRepoBranch
        );
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
    document.querySelectorAll('#linkgenerator input[type="radio"]').forEach(
        function (element) {
            element.addEventListener('change', render);
        }
    )
    document.querySelectorAll('#linkgenerator input[type="text"], #linkgenerator input[type="url"]').forEach(
        function (element) {
            element.addEventListener('input', render);
        }
    )

    populateFromQueryString();

    // Do an initial render, to make sure our disabled / enabled properties are correctly set
    render();
}

window.onload = main;