// This script contains the code that creates the central network, as well as
// a function for resetting it to a brand new page.
var nodes, edges, network; //Global variables
var startpages = [];
// Tracks whether the network needs to be reset. Used to prevent deleting nodes
// when multiple nodes need to be created, because AJAX requests are async.
var needsreset = true;
var container = document.getElementById('namecontainer');
//Global options
var options = {
    autoResize: true,
    height: '100%',
    width: '100%',
    nodes: {
        shape: 'dot',
        scaling: { min: 20,max: 30,
            label: { min: 14, max: 30, drawThreshold: 9, maxVisible: 20 }
        },
        font: {size: 14, face: 'Helvetica Neue, Helvetica, Arial'}
    },
    interaction: {
        hover: true,
        hoverConnectedEdges: false,
        selectConnectedEdges: true,
    },
};

var nodes = new vis.DataSet();
var edges = new vis.DataSet();
var data = {nodes: nodes, edges: edges};
var initialized = false;


//Make the network
function makeNetwork() {
    network = new vis.Network(container, data, options);
    bindNetwork();
    initialized = true;
}


// Reset the network to be new each time.
function resetNetwork(start) {
    if (!initialized) makeNetwork();
    console.log("Creation of the first node");
    // var startID = getNeutralId(start);
    // debugger;
    var startID = Object.keys(start)[0];
    console.log("First value is " + startID);
    startpages.push(startID); // Register the page as an origin node
    tracenodes = [];
    traceedges = [];

    // Change "go" button to a refresh icon
    // -- CREATE NETWORK -- //
    //Make a container
    // {id: startID, label: wordwrap(decodeURIComponent(start), 20),
    // parent below actually has current value
    // {id: startID, label: startID, value: 2, level: 0, color: getColor(0), x: 0, y: 0, parent: startID}//Parent is self
    // {id: startID, label: (startID, 20), value: 2, level: 0, color: getColor(0), x: 0, y: 0, parent: startID}//Parent is self
    nodes = new vis.DataSet([
        {id: startID, label: startID, value: 2, level: 0, color: getColor(0), x: 0, y: 0, parent: startID, node_parent_marker: start[startID]}// Pass object
    ]);
    edges = new vis.DataSet();
    //Put the data in the container
    data = {nodes: nodes, edges: edges};
    network.setData(data);
    document.getElementById("namecontainer").setAttribute("name", startID);
}


// Add a new start node to the map.
// maybe index isn't used
// function addStart(start, index) {
function addStart(start) {
    // probably uses the needsreset from the global space
    // console.log("Index value at addStart is " + index);
    // If the first time
    // debugger;
    if (needsreset) {
        // Delete everything only for the first call to addStart by tracking needsreset
        resetNetwork(start);
        needsreset = false;
        return;
    }
    // so far haven't tested this yet
    else {
        console.log("Add start but doesn't need reset");
        // var startID = getNeutralId(start);
        var startID = Object.keys(start)[0];
        console.log("Another value is " + startID);
        startpages.push(startID);
        nodes.add([
          {id: startID, label: startID.replace("_", " "), value: 2, level: 0, color: getColor(0), x: 0, y: 0, parent: startID, node_parent_marker: start[startID]}
        ]);
    }
}


// Reset the network with the content from the input box.
function resetNetworkFromInput(graphNodes) {
    console.log('This is called from bindings js file. In main js');
    // Network should be reset
    needsreset = true;
    // var cf = document.getElementsByClassName("commafield")[0];
    // console.log("This is value of commafield in main js resetNetworkFromInput == " + cf);
    // Items entered.
    // (Future) should restrict this to a single item
    // var inputs = getItems(cf);
    var inputs = graphNodes; // redundant?
    // If no input is given, prompt user to enter articles
    // if (!inputs[0]) {
    //     noInputDetected();
    //     return;
    // }
    if (jQuery.isEmptyObject(inputs)) {
        noInputDetected();
        return;
    }
    // code I added
    // get rid of the commas and whatever
    // debugger;
    // var input_nodes = Object.keys(inputs);
    // debugger;
    for (var key in inputs) {
        // if (jQuery.isEmptyObject(inputs[key])) {
        //     var temp = {};
        //     temp[key] = {};
        //     addStart(temp);    // empty object case
        // }
        // else {
        var temp = {};
        temp[key] = inputs[key];
        addStart(temp);  // call for each independent node
        // }
    }
    // for (var i = 0; i < inputs.length; i++) {
    //     getPageName(encodeURI(inputs[i]), addStart);
    // }
}

// Reset the network with content from a JSON string
function resetNetworkFromJson(data) {
  if (!initialized) makeNetwork();
  var obj = networkFromJson(data);
  nodes = obj.nodes;
  edges = obj.edges;
  startpages = obj.startpages;
  // Fill the network
  network.setData({nodes: nodes, edges: edges});
  // Populate the top bar
  for (var i = 0; i < startpages.length; i++) {
    addItem(document.getElementById("input"), nodes.get(startpages[i]).label);
  }
  // Transform the "go" button to a "refresh" button
  document.getElementById("submit").innerHTML = '<i class="icon ion-refresh"> </i>';
}
