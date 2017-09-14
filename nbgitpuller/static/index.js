require([
    'jquery',
    'base/js/utils',
    'components/xterm.js/dist/xterm'
], function(
    $,
    utils,
    Terminal
) {


    function GitSync(baseUrl, repo, branch, path) {
        // Class that talks to the API backend & emits events as appropriate
        this.baseUrl = baseUrl;
        this.repo = repo;
        this.branch = branch;
        this.path = path;

        if (path.endsWith('.ipynb')) {
            this.redirectUrl = baseUrl + 'notebooks/' + path;
        } else {
            this.redirectUrl = baseUrl + 'tree/' + path;
        }

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
        var syncUrl = this.baseUrl + 'git-pull/api?' + $.param({
            repo: this.repo,
            branch: this.branch,
            path: this.path
        });

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
        this.visible = false;
        this.term.open($(termSelector)[0]);
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
        this._fitTerm();
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

    GitSyncView.prototype._fitTerm = function() {
        // Vendored in from the xterm.js fit addon
        // Because I can't for the life of me get the addon to be
        // actually included here as an require.js thing.
        // And life is too short.
        var term = this.term;
        if (!term.element.parentElement) {
            return null;
        }
        var parentElementStyle = window.getComputedStyle(term.element.parentElement),
            parentElementHeight = parseInt(parentElementStyle.getPropertyValue('height')),
            parentElementWidth = Math.max(0, parseInt(parentElementStyle.getPropertyValue('width')) - 17),
            elementStyle = window.getComputedStyle(term.element),
            elementPaddingVer = parseInt(elementStyle.getPropertyValue('padding-top')) + parseInt(elementStyle.getPropertyValue('padding-bottom')),
            elementPaddingHor = parseInt(elementStyle.getPropertyValue('padding-right')) + parseInt(elementStyle.getPropertyValue('padding-left')),
            availableHeight = parentElementHeight - elementPaddingVer,
            availableWidth = parentElementWidth - elementPaddingHor,
            container = term.rowContainer,
            subjectRow = term.rowContainer.firstElementChild,
            contentBuffer = subjectRow.innerHTML,
            characterHeight,
            rows,
            characterWidth,
            cols,
            geometry;

        subjectRow.style.display = 'inline';
        subjectRow.innerHTML = 'W'; // Common character for measuring width, although on monospace
        characterWidth = subjectRow.getBoundingClientRect().width;
        subjectRow.style.display = ''; // Revert style before calculating height, since they differ.
        characterHeight = subjectRow.getBoundingClientRect().height;
        subjectRow.innerHTML = contentBuffer;

        rows = parseInt(availableHeight / characterHeight);
        cols = parseInt(availableWidth / characterWidth);

        term.resize(cols, rows);
    };

    var gs = new GitSync(
        utils.get_body_data('baseUrl'),
        utils.get_body_data('repo'),
        utils.get_body_data('branch'),
        utils.get_body_data('path')
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
});
