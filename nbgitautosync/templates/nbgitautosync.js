require([
    'jquery',
    'base/js/utils',
    'xterm.js'
], function($, utils, Terminal) {
    function redirect_url() {
        var path = utils.get_body_data('path');
        if (path.endsWith('.ipynb')) {
            return utils.get_body_data('baseUrl') + 'notebooks/' + path;
        } else {
            return utils.get_body_data('baseUrl') + 'tree/' + path;
        }
    }

    var base_url = utils.get_body_data('baseUrl');
    console.log(base_url);

    var sync_url = base_url + 'sync-repo?' + $.param({
        repo: utils.get_body_data('repo'),
        branch: utils.get_body_data('branch'),
        path: utils.get_body_data('path')
    });

    var term = new Terminal();
    term.open($('#pull-status')[0]);

    var es = new EventSource(sync_url);
    es.addEventListener('message', function(ev) {
        var data = JSON.parse(ev.data);
        if (data.phase == 'Finished') {
            es.close();
            window.location.href = redirect_url();
        } else if (data.phase == 'Syncing') {
            term.write(data.output);
        }
    });
    $('#header, #site').show();
});
