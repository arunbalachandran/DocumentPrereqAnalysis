// This script contains the big functions that implement a lot of the core
// functionality, like expanding nodes, and getting the nodes for a traceback.


// -- GLOBAL VARIABLES -- //
var isReset = true;
var selectedNode = null;
var traceedges = [];
var tracenodes = [];
// ---------------------- //
var first_time = 1;

// AJAX callback to add to a node once data is received
// I think data is the subchild
// function expandNodeCallback(page, data) {
function expandNodeCallback(page) {
    var node = nodes.get(page);  //The node that was clicked
    var level = node.level + 1;  //Level for new nodes is one more than parent
    // var parentObj = node.get(page);
    console.log("Parent object is ", nodes.get(page)['node_parent_marker']);
    var subpages = node['node_parent_marker'];   // list of child nodes
    console.log("THe current level for node that was clicked " + node.level);
    console.log("THe current node that was clicked ", node.label);
    document.getElementById("namecontainer").setAttribute("name", node.label);
    LoadGoogle();
    console.log("Subpages are ", subpages);
    // Add all children to network
    var subnodes = [];
    var newedges = [];
    // Where new nodes should be spawned
    var nodeSpawn = getSpawnPosition(page);
    //Create node objects
    // debugger;
    for (var key in subpages) {
        console.log("Loop ran");
        console.log("Key is ", key);
        // key wont fetch the object duh!
        var subpage = key;
        // var subpage = Object.keys(key)[0];
        // var subpageID = getNeutralId(subpage);
        var subpageID = subpage;
        // debugger;
        if (nodes.getIds().indexOf(subpageID) == -1) {        //Don't add if node exists
            subnodes.push({id: subpageID, label: subpage.replace(/_/g, ' '), value: 1, level: level, color: getColor(level), parent: page,
                           node_parent_marker: nodes.get(page)['node_parent_marker'][key], x: nodeSpawn[0], y: nodeSpawn[1]});  //Add node
            // subnodes.push({id: subpageID, label: wordwrap(decodeURIComponent(subpage),15), value: 1,
            //                level: level, color: getColor(level), parent: page,
            //                x: nodeSpawn[0], y: nodeSpawn[1]});  //Add node
        }

        if (!getEdgeConnecting(page, subpageID)) {            //Don't create duplicate edges in same direction
            newedges.push({from: page, to: subpageID, color: getEdgeColor(level),
                           level: level, selectionWidth: 2, hoverWidth: 0});
        }
    }
    console.log("Done with loop");
    //Add the stuff to the nodes array
    nodes.add(subnodes);
    edges.add(newedges);
}
//Expand a node without freezing other stuff
function expandNode(page) {
    // var label = nodes.get(page).label;
    // console.log("label for page is " + label);
    // var pagename = encodeURIComponent(unwrap(label));
    // var pagename = graphNodes[page];
    // if (pagename in )
    // var data = graphNodes[page];
    expandNodeCallback(page);
    // expandNodeCallback(page, data);
    // getSubPages(pagename, function(data) {expandNodeCallback(page, data);});
}

//Get all the nodes tracing back to the start node.
function getTraceBackNodes(node) {
    var finished = false;
    var path = [];

    // debugger;
    while (! finished) { //Add parents of nodes until we reach the start
        path.push(node);
        if (startpages.indexOf(node) !== -1) { //Check if we've reached the end
        // My amazing condition
            console.log("Current parent of node ", nodes.get(node).label, " is ", nodes.get(node).parent);
        // if (startpages[0] === nodes.get(node).parent) {
            finished = true;
        }
        console.log("Now get the parent ", nodes.get(node).parent);
        node = nodes.get(node).parent; //Keep exploring with the node above.
    }
    return path;
}

//Get all the edges tracing back to the start node.
function getTraceBackEdges(tbnodes) {
  tbnodes.reverse();
  var path = [];
  for (var i=0; i<tbnodes.length-1; i++) { //Don't iterate through the last node
    path.push( getEdgeConnecting(tbnodes[i], tbnodes[i+1]) );
  }
  return path;
}

//Reset the color of all nodes, and width of all edges.
function resetProperties() {
  if (!isReset) {
    selectedNode = null;
    //Reset node color
    var modnodes = tracenodes.map(function(i){return nodes.get(i);});
    colorNodes(modnodes, 0);
    //Reset edge width and color
    var modedges = traceedges.map(function(i){
      var e=edges.get(i);
      e.color=getEdgeColor(nodes.get(e.to).level);
      return e;
    });
    edgesWidth(modedges, 1);
    tracenodes = [];
    traceedges = [];
  }
}

//Highlight the path from a given node back to the central node.
function traceBack(node) {
    if (node != selectedNode) {
        selectedNode = node;
        resetProperties();
        tracenodes = getTraceBackNodes(node);
        traceedges = getTraceBackEdges(tracenodes);
        //Color nodes yellow
        var modnodes = tracenodes.map(function(i){return nodes.get(i);});
        colorNodes(modnodes, 1);
        //Widen edges
        var modedges = traceedges.map(function(i){
        var e=edges.get(i);
        e.color={inherit:"to"};
        return e;
        });
        edgesWidth(modedges, 5);
    }
}
