// DESERIALIZATION METHODS //
// Unabbreviate a node Object
function unabbreviateNode(node, startpgs) {
    // Make quick substitutions
    var newnode = {label: node.a,
                   level: node.b,
                   parent: node.c};
    // Infer omitted properties
    newnode.id = getNeutralId(newnode.label);
    newnode.color = getColor(newnode.level);
    newnode.value = startpgs.indexOf(newnode.id) === -1 ? 1:2;
    return newnode;
}

// Reconstruct edges given a list of nodes
function buildEdges (nds) {
    var edgs = new vis.DataSet();
    for (var i = 0; i < nds.length; i++) {
        node = nds[i];
        if (node.parent != node.id) { // Don't create an edge from start nodes to themselves
            edgs.add({from: node.parent, to: node.id, color: getEdgeColor(node.level),
                      level: node.level, selectionWidth: 2, hoverWidth:0});
        }
    }
    return edgs;
}

// Take consise JSON and use it to reconstruct `nodes` and `edges`
function networkFromJson(data) {
    // Get data
    data = JSON.parse(data);
    out = {};
    // Store startpages
    out.startpages = data.startpages;
    // Store nodes
    var nds = data.nodes;
    var expandedNodes = nds.map(function(x){return unabbreviateNode(x, out.startpages);});
    out.nodes = new vis.DataSet();
    out.nodes.add(expandedNodes);
    // Store edges
    out.edges = buildEdges(expandedNodes);
    out.edges.add(data.edges);
    return out;
}
