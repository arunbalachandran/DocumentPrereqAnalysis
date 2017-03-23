// This script contains the code necessary to make requests to the python API,
// as well as a more general function which is also used to fetch the README
// for rendering.



// GLOBALS

var api_endpoint = "http://localhost:5000/";



// BASIC METHODS

//Make an asynchronous GET request and execute the onSuccess callback with the data
function requestPage(url, onSuccess) {
    onSuccess = onSuccess || function(){};
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (xhttp.readyState == 4 && xhttp.status == 200) {
            console.log("Response for page title from wikipedia (ajax) " + xhttp.responseText);
            onSuccess(xhttp.responseText);
        }
    };
    xhttp.open("GET", url, true);
    xhttp.send();
}

// Send an AJAX GET request to the server, passing the name of a Wikipedia page
function apiRequest(api, page, onSuccess) {
    console.log("This is api request to get subpages");
    var url = api_endpoint + api + "?page=" + page;
    requestPage(url, function (data) {
        console.log(JSON.parse(data));
        onSuccess(JSON.parse(data));
    });
}

// API calls
// WIKIPEDIA PARSING ----------

// Get the name of all pages linked to by a page
function getSubPages(page, onSuccess) {
    apiRequest("links", page, onSuccess);
}

//Get the name of the wikipedia article for a query
// function getPageName(query, onSuccess) {
//     apiRequest("pagename", query, onSuccess);
// }
