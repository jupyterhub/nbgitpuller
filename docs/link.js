// Pure function that generates an nbgitpuller URL
function generateUrl(hubUrl, urlPath, repoUrl, branch) {

    // assume hubUrl is a valid URL
    var url = new URL(hubUrl);
   
    url.searchParams.set('repo', repoUrl);

    if (urlPath)  {
        url.searchParams.set('urlpath', urlPath);
    }

    if (branch) {
        url.searchParams.set('branch', branch);
    }

    url.pathname += 'hub/user-redirect/git-pull';

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

function displayLink() {
    var form = document.getElementById('linkgenerator');

    form.classList.add('was-validated');
    if (form.checkValidity()) {
        var hubUrl = document.getElementById('hub').value;
        var repoUrl = document.getElementById('repo').value;
        var filePath = document.getElementById('filepath').value;
        var branch = document.getElementById('branch').value;
        var appName = form.querySelector('input[name="app"]:checked').value;

        if (appName === 'custom') {
            var urlPath = document.getElementById('urlpath').value;
        } else {
            var urlPath = apps[appName].generateUrlPath(filePath);
        }

        document.getElementById('link').value = generateUrl(
            hubUrl, urlPath, repoUrl, branch
        );
    }
}
function populateFromQueryString() {
    // preseed values if specified in the url
    var params = new URLSearchParams(window.location.search);
    // Parameters are read from query string, and <input> fields are set to them
    var allowedParams = ['hub', 'repo', 'branch'];
    for (var i=0; i < allowedParams.length; i++) {
        var param = allowedParams[i];
        if (params.has(param)) {
            document.getElementById(param).value = params.get(param);
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
        function(element) { 
            element.addEventListener('change', render);
        }
    )
    document.querySelectorAll('#linkgenerator input[type="text"], #linkgenerator input[type="url"]').forEach(
        function(element) { 
            element.addEventListener('input', render);
        }
    )

    populateFromQueryString();

    // Do an initial render, to make sure our disabled / enabled properties are correctly set
    render();
}

window.onload = main;