
import { Terminal } from 'xterm';
import { FitAddon } from 'xterm-addon-fit';
import { WebLinksAddon } from 'xterm-addon-web-links';

export class GitSyncView{
    constructor(termSelector, progressSelector, termToggleSelector) {
        // Class that encapsulates view rendering as much as possible
        this.term = new Terminal({
            convertEol: true
        });
        this.fit = new FitAddon();
        this.term.loadAddon(this.fit);
        this.term.loadAddon(new WebLinksAddon());

        this.visible = false;
        this.progress = document.querySelector(progressSelector);

        this.termToggle = document.querySelector(termToggleSelector);
        this.termElement = document.querySelector(termSelector);

        this.termToggle.onclick = () => this.setTerminalVisibility(!this.visible)
    }

    setTerminalVisibility(visible) {
        if (visible) {
            this.termElement.parentElement.classList.remove('hidden');
        } else {
            this.termElement.parentElement.classList.add('hidden');
        }
        this.visible = visible;
        if (visible) {
            // See https://github.com/jupyterhub/nbgitpuller/pull/46 on why this is here.
            if (!this.term.element) {
                this.term.open(this.termElement);
            }
            this.fit.fit();
        }
    }

    setProgressValue(val) {
        this.progress.setAttribute('aria-valuenow', val);
        this.progress.style.width = val + '%';
    }

    getProgressValue() {
        return parseFloat(this.progress.getAttribute('aria-valuenow'));
    }

    setProgressText(text) {
        this.progress.querySelector('span').innerText = text;
    }

    getProgressText() {
        return this.progress.querySelector('span').innerText;
    }

    setProgressError(isError) {
        if (isError) {
            this.progress.classList.add('progress-bar-danger');
        } else {
            this.progress.classList.remove('progress-bar-danger');
        }
    }
}
