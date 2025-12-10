
import { Terminal } from 'xterm';
import { FitAddon } from 'xterm-addon-fit';
import { WebLinksAddon } from 'xterm-addon-web-links';
import { GitError } from './giterror';

export class GitSyncView{
    constructor(termSelector, progressSelector, termToggleSelector, containerErrorSelector, copyErrorSelector, containerErrorHelpSelector) {
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
        this.containerError = document.querySelector(containerErrorSelector);
        this.copyError = document.querySelector(copyErrorSelector);
        this.containerErrorHelp = document.querySelector(containerErrorHelpSelector);

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

    setContainerError(isError, errorOutput='', errorMessage='') {
        if (isError) {
            this.containerError.classList.toggle('hidden', !this.visible);
            const button = this.copyError;
            button.onclick = async () => {
                try {
                    await navigator.clipboard.writeText(errorOutput);
                    button.innerHTML = 'Error message copied!';
                } catch (err) {
                    console.error('Failed to copy error text: ', err);
                }
            }
            const errorHelp = GitError(errorMessage);
            if (errorHelp) {
                this.containerErrorHelp.innerHTML = errorHelp;
                this.termElement.parentElement.classList.add('hidden');
            }
        }
    }
}
