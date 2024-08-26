import { GitSync  } from './gitsync';
import { GitSyncView } from './gitsyncview';
import css from '../../../node_modules/xterm/css/xterm.css';

const getBodyData = (key) => {
    /**
     * get a url-encoded item from body.data and decode it
     * we should never have any encoded URLs anywhere else in code
     * until we are building an actual request
     */
    if(!document.body.hasAttribute('data-' + key)) {
        return undefined;
    }
    let val = document.body.getAttribute('data-' + key);
    return decodeURIComponent(val);
};

const gs = new GitSync(
    getBodyData('base-url'),
    getBodyData('repo'),
    getBodyData('branch'),
    getBodyData('depth'),
    getBodyData('targetpath'),
    getBodyData('path'),
    getBodyData('xsrf'),
);

const gsv = new GitSyncView(
    '#status-details',
    '#status-panel-title',
    '#status-panel-toggle'
);

gs.addHandler('syncing', function(data) {
    gsv.term.write(data.output);
});
gs.addHandler('finished', function() {
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

// Make sure we provide plenty of appearances of progress!
let progressTimers = [];
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


const substatus_messages = [
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
