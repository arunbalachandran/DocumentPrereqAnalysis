// This script contains (most of) the code that binds actions to events.
//Functions that will be used as bindings
function expandEvent (params) {     // Expand a node (with event handler)
    if (params.nodes.length) {      //Did the click occur on a node?
        console.log("params for the nodes are ", params.nodes);
        var page = params.nodes[0]; //The id of the node clicked
        console.log("Expanding page " + page);
        expandNode(page);
    }
}

function mobileTraceEvent (params) { // Trace back a node (with event handler)
    console.log("Mobile trace event occured");
    if (params.nodes.length) { //Was the click on a node?
        //The node clicked
        var page = params.nodes[0];
        //Highlight in blue all nodes tracing back to central node
        traceBack(page);
    }
    else {
        resetProperties();
    }
}

function openPageEvent (params) {
    if (params.nodes.length) {
        console.log("A double click occured on node ", params.nodes[0]);
        var nodeid = params.nodes[0];
        var page = encodeURIComponent(unwrap(nodes.get(nodeid).label));
        var url = "http://en.wikipedia.org/wiki/"+page;
        window.open(url, '_blank');
    }
}

// Bind the network events
// function that is invoked on button click
function bind() {
    // Prevent iOS scrolling
    document.ontouchmove = function(event){
        event.preventDefault();
    };
    console.log("This is a call from the bind function");
    console.log("Got graph nodes " + JSON.stringify(graphNodes));
    // Bind actions for search component.
    // var cf = document.getElementsByClassName("commafield")[0];
    //Bind the action of pressing the button
    // var submitButton = document.getElementById('submit');
    // submitButton.onclick = function() {
    // console.log("This is on submit button click.");
    // shepherd.cancel(); // Dismiss the tour if it is in progress
    resetNetworkFromInput(graphNodes);  // reset the tree network - main.js
    // };

    // Bind tour start
    // var tourbtn = document.getElementById("tourinit");
    // tourbtn.onclick = function() {shepherd.start();};
    //
    // // Bind GitHub button
    // var ghbutton = document.getElementById("github");
    // ghbutton.onclick = function(event) {
    //     window.open("https://github.com/The-Penultimate-Defenestrator/wikipedia-map");
    // };
    //
    // // Bind twitter button
    // var sharebutton = document.getElementById("share");
    // var buttons = document.getElementById("buttons");
    // sharebutton.onclick = function(event) {
    //
    // };
}

// Deals with node expansion on click
// Don't deal with it in the start
function bindNetwork() {
    if (isTouchDevice) { // Device has a touchscreen
        network.on("hold", expandEvent);       // Long press to expand
        network.on("click", mobileTraceEvent); // Highlight traceback on click
    }
    else {               // Device does not have a touchscreen
        network.on("click", expandEvent); // Expand on click
        console.log("Expand click here");
        network.on("hoverNode", function(params) { // Highlight traceback on hover
            traceBack(params.node);
        });
        network.on("blurNode", resetProperties); // un-traceback on un-hover
    }
    // Bind double-click to open page
    network.on("doubleClick", openPageEvent);
}
