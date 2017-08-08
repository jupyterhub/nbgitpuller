require([
    'jquery',
    'base/js/utils',
    'git-sync/static/xterm.js-2.9.1/dist/xterm.js'
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

    var sync_url = base_url + 'git-sync/api?' + $.param({
        repo: utils.get_body_data('repo'),
        branch: utils.get_body_data('branch'),
        path: utils.get_body_data('path')
    });

    var term = new Terminal({
        convertEol: true,
        disableStdin: true
    });
    term.open($('#pull-status')[0]);

    var es = new EventSource(sync_url);
    es.addEventListener('message', function(ev) {
        var data = JSON.parse(ev.data);
        if (data.phase == 'Finished') {
            es.close();
            // window.location.href = redirect_url();
        } else if (data.phase == 'Syncing') {
            term.write(data.output);
        }
    });
    $('#header, #site').show();

    // Make sure we provide plenty of appearances of progress!
    setInterval(function() {
        $('#sub-status').text(substatus_messages[Math.floor(Math.random() * substatus_messages.length)]);
    }, 3000);
    setInterval(function() {
        $('#sub-status').text($('#sub-status').text() + '.');
    }, 800);
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
        "Deunionizing Bulldozers",
        "Dicing Models",
        "Diluting Livestock Nutrition Variables",
        "Downloading Satellite Terrain Data",
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
        "Initializing My Sim Tracking Mechanism",
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
        "Pixalating Nude Patch",
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
        "Zeroing Crime Network",
    ];
});
