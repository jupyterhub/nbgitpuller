import { Terminal } from 'xterm';
import { FitAddon } from 'xterm-addon-fit';
import css from '../../../node_modules/xterm/css/xterm.css';

function GitSync(baseUrl, repo, branch, depth, targetpath, path) {
    // Class that talks to the API backend & emits events as appropriate
    this.baseUrl = baseUrl;
    this.repo = repo;
    this.branch = branch;
    this.depth = depth;
    this.targetpath = targetpath;
    this.redirectUrl = baseUrl + path;

    this.callbacks = {};
}

GitSync.prototype.addHandler = function(event, cb) {
    if (this.callbacks[event] == undefined) {
        this.callbacks[event] = [cb];
    } else {
        this.callbacks[event].push(cb);
    }
};

GitSync.prototype._emit = function(event, data) {
    if (this.callbacks[event] == undefined) { return; }
    $.each(this.callbacks[event], function(i, ev) {
        ev(data);
    });
};


GitSync.prototype.start = function() {
    // Start git pulling handled by SyncHandler, declared in handlers.py
    var syncUrlParams = {
        repo: this.repo,
        targetpath: this.targetpath
    }
    if (typeof this.depth !== 'undefined' && this.depth != undefined) {
        syncUrlParams['depth'] = this.depth;
    }
    if (typeof this.branch !== 'undefined' && this.branch != undefined) {
        syncUrlParams['branch'] = this.branch;
    }
    var syncUrl = this.baseUrl + 'git-pull/api?' + $.param(syncUrlParams);

    this.eventSource = new EventSource(syncUrl);
    var that = this;
    this.eventSource.addEventListener('message', function(ev) {
        var data = JSON.parse(ev.data);
        if (data.phase == 'finished' || data.phase == 'error') {
            that.eventSource.close();
        }
        that._emit(data.phase, data);
    });
    this.eventSource.addEventListener('error', function(error) {
        console.log(arguments);
        that._emit('error', error);
    });
};

function GitSyncView(termSelector, progressSelector, termToggleSelector) {
    // Class that encapsulates view rendering as much as possible
    this.term = new Terminal({
        convertEol: true
    });
    this.fit = new FitAddon();
    this.term.loadAddon(this.fit);

    this.visible = false;
    this.$progress = $(progressSelector);

    this.$termToggle = $(termToggleSelector);
    this.termSelector = termSelector;

    var that = this;
    this.$termToggle.click(function() {
        that.setTerminalVisibility(!that.visible);
    });
}

GitSyncView.prototype.setTerminalVisibility = function(visible) {
    if (visible) {
        $(this.termSelector).parent().removeClass('hidden');
    } else {
        $(this.termSelector).parent().addClass('hidden');
    }
    this.visible = visible;
    if (visible) {
        // See https://github.com/jupyterhub/nbgitpuller/pull/46 on why this is here.
        if (!this.term.element) {
            this.term.open($(this.termSelector)[0]);
        }
        this.fit.fit();
    }

}

GitSyncView.prototype.setProgressValue = function(val) {
    this.$progress.attr('aria-valuenow', val);
    this.$progress.css('width', val + '%');
};

GitSyncView.prototype.getProgressValue = function() {
    return parseFloat(this.$progress.attr('aria-valuenow'));
};

GitSyncView.prototype.setProgressText = function(text) {
    this.$progress.children('span').text(text);
};

GitSyncView.prototype.getProgressText = function() {
    return this.$progress.children('span').text();
};

GitSyncView.prototype.setProgressError = function(isError) {
    if (isError) {
        this.$progress.addClass('progress-bar-danger');
    } else {
        this.$progress.removeClass('progress-bar-danger');
    }
};

var get_body_data = function(key) {
    /**
     * get a url-encoded item from body.data and decode it
     * we should never have any encoded URLs anywhere else in code
     * until we are building an actual request
     */
    var val = $('body').data(key);
    if (typeof val === 'undefined')
        return val;
    return decodeURIComponent(val);
};

var gs = new GitSync(
    get_body_data('baseUrl'),
    get_body_data('repo'),
    get_body_data('branch'),
    get_body_data('depth'),
    get_body_data('targetpath'),
    get_body_data('path')
);

var gsv = new GitSyncView(
    '#status-details',
    '#status-panel-title',
    '#status-panel-toggle'
);

gs.addHandler('syncing', function(data) {
    gsv.term.write(data.output);
});
gs.addHandler('finished', function(data) {
    progressTimers.forEach(function(timer)  { clearInterval(timer); });
    gsv.setProgressValue(100);
    gsv.setProgressText('Sync finished, redirecting...');
    window.location.href = gs.redirectUrl;
});
gs.addHandler('error', function(data) {
    progressTimers.forEach(function(timer)  { clearInterval(timer); });
    gsv.setProgressValue(100);
    gsv.setProgressText('Error: ' + data.message);
    gsv.setProgressError(true);
    gsv.setTerminalVisibility(true);
    if (data.output) {
        gsv.term.write(data.output);
    }
});
gs.start();

$('#header, #site').show();

// Make sure we provide plenty of appearances of progress!
var progressTimers = [];
progressTimers.push(setInterval(function() {
    gsv.setProgressText(substatus_messages[Math.floor(Math.random() * substatus_messages.length)]);
}, 3000));
progressTimers.push(setInterval(function() {
    gsv.setProgressText(gsv.getProgressText() + '.');
}, 800));

progressTimers.push(setInterval(function() {
    // Illusion of progress!
    gsv.setProgressValue(gsv.getProgressValue() + (0.01 * (100 - gsv.getProgressValue())));
}, 900));


var substatus_messages = [
    "Adding Hidden Agendas",
    "Adjusting Bell Curves",
    "Aesthesizing Industrial Areas",
    "Aligning Covariance Matrices",
    "Applying Feng Shui Shaders",
    "Applying Theatre Soda Layer",
    "Asserting Packed Exemplars",
    "Attempting to Lock Back-Buffer",
    "Binding Sapling Root System",
    "Breeding Fauna",
    "Building Data Trees",
    "Bureacritizing Bureaucracies",
    "Calculating Inverse Probability Matrices",
    "Calculating Llama Expectoration Trajectory",
    "Calibrating Blue Skies",
    "Charging Ozone Layer",
    "Coalescing Cloud Formations",
    "Cohorting Exemplars",
    "Collecting Meteor Particles",
    "Compounding Inert Tessellations",
    "Compressing Fish Files",
    "Computing Optimal Bin Packing",
    "Concatenating Sub-Contractors",
    "Containing Existential Buffer",
    "Debarking Ark Ramp",
    "Debunching Unionized Commercial Services",
    "Deciding What Message to Display Next",
    "Decomposing Singular Values",
    "Decrementing Tectonic Plates",
    "Deleting Ferry Routes",
    "Depixelating Inner Mountain Surface Back Faces",
    "Depositing Slush Funds",
    "Destabilizing Economic Indicators",
    "Determining Width of Blast Fronts",
    "Dicing Models",
    "Diluting Livestock Nutrition Variables",
    "Downloading Satellite Terrain Data",
    "Eating Ice Cream",
    "Exposing Flash Variables to Streak System",
    "Extracting Resources",
    "Factoring Pay Scale",
    "Fixing Election Outcome Matrix",
    "Flood-Filling Ground Water",
    "Flushing Pipe Network",
    "Gathering Particle Sources",
    "Generating Jobs",
    "Gesticulating Mimes",
    "Graphing Whale Migration",
    "Hiding Willio Webnet Mask",
    "Implementing Impeachment Routine",
    "Increasing Accuracy of RCI Simulators",
    "Increasing Magmafacation",
    "Initializing Rhinoceros Breeding Timetable",
    "Initializing Robotic Click-Path AI",
    "Inserting Sublimated Messages",
    "Integrating Curves",
    "Integrating Illumination Form Factors",
    "Integrating Population Graphs",
    "Iterating Cellular Automata",
    "Lecturing Errant Subsystems",
    "Modeling Object Components",
    "Normalizing Power",
    "Obfuscating Quigley Matrix",
    "Overconstraining Dirty Industry Calculations",
    "Partitioning City Grid Singularities",
    "Perturbing Matrices",
    "Polishing Water Highlights",
    "Populating Lot Templates",
    "Preparing Sprites for Random Walks",
    "Prioritizing Landmarks",
    "Projecting Law Enforcement Pastry Intake",
    "Realigning Alternate Time Frames",
    "Reconfiguring User Mental Processes",
    "Relaxing Splines",
    "Removing Road Network Speed Bumps",
    "Removing Texture Gradients",
    "Removing Vehicle Avoidance Behavior",
    "Resolving GUID Conflict",
    "Reticulating Splines",
    "Retracting Phong Shader",
    "Retrieving from Back Store",
    "Reverse Engineering Image Consultant",
    "Routing Neural Network Infanstructure",
    "Scattering Rhino Food Sources",
    "Scrubbing Terrain",
    "Searching for Llamas",
    "Seeding Architecture Simulation Parameters",
    "Sequencing Particles",
    "Setting Advisor Moods",
    "Setting Inner Deity Indicators",
    "Setting Universal Physical Constants",
    "Smashing The Patriarchy",
    "Sonically Enhancing Occupant-Free Timber",
    "Speculating Stock Market Indices",
    "Splatting Transforms",
    "Stratifying Ground Layers",
    "Sub-Sampling Water Data",
    "Synthesizing Gravity",
    "Synthesizing Wavelets",
    "Time-Compressing Simulator Clock",
    "Unable to Reveal Current Activity",
    "Weathering Buildings",
    "Zeroing Crime Network"
];
