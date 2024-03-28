export class GitSync {
    constructor(baseUrl, repo, branch, depth, targetpath, path, xsrf) {
        // Class that talks to the API backend & emits events as appropriate
        this.baseUrl = baseUrl;
        this.repo = repo;
        this.branch = branch;
        this.depth = depth;
        this.targetpath = targetpath;
        this.redirectUrl = baseUrl + path;
        this._xsrf = xsrf;

        this.callbacks = {};
    }

    addHandler(event, cb) {
        if (this.callbacks[event] == undefined) {
            this.callbacks[event] = [cb];
        } else {
            this.callbacks[event].push(cb);
        }
    }

    _emit(event, data) {
        if (this.callbacks[event] == undefined) { return; }
        for(let ev of this.callbacks[event]) {
            ev(data);
        }

    }

    start() {
        // Start git pulling handled by SyncHandler, declared in handlers.py
        let syncUrlParams = new URLSearchParams({
            _xsrf: this._xsrf,
            repo: this.repo,
            targetpath: this.targetpath
        });
        if (typeof this.depth !== 'undefined' && this.depth != undefined) {
            syncUrlParams.append('depth', this.depth);
        }
        if (typeof this.branch !== 'undefined' && this.branch != undefined) {
            syncUrlParams.append('branch', this.branch);
        }
        const syncUrl = this.baseUrl + 'git-pull/api?' + syncUrlParams.toString();

        this.eventSource = new EventSource(syncUrl);
        this.eventSource.addEventListener('message', (ev) => {
            const data = JSON.parse(ev.data);
            if (data.phase == 'finished' || data.phase == 'error') {
                this.eventSource.close();
            }
            this._emit(data.phase, data);
        });
        this.eventSource.addEventListener('error',(error) => {
            this._emit('error', error);
        });
    }
}
