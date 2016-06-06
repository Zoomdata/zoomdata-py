/*accountID, collection, headers, connReq, 
  sourceReq are dinamic variables passed by the ZD obj*/
var createSource = function() {
    if(collection == ''){
      $('#result').html("<p>Please enter a MongoDB collection name</p>");
    } else {
        $('#result').html('<p>Creating Zoomdata Source with name <b>' + collection + '</b>...</p>');
        // for now, the ZD connection name is the same as the collection name
        // an improvement is to re-use the ZD connectin for additional sources
        //If a conn name is not specified, then the same name of the 
        //collection will be used
       connReq.name = connectionName;

     //At some point this url will have to be configurable
      $.ajax({
          url: 'https://pubsdk.zoomdata.com:8443/zoomdata/api/accounts/' + accountID + '/connections',
          type: 'post',
          data: JSON.stringify(connReq),
          // credentials should be passed
          headers: headers,
          dataType: 'json',
          success: function (connResponse) {
              $('#result').html('<p>Logging response</p><div>' + JSON.stringify(connResponse) + ' </div>');
               callCreateSource(connResponse, collection);
          },
          error: function (request, status, error) {
              alert(request.responseText);
          }
      });
    }
}

var callCreateSource = function(connResponse, collectionName) {
    var sourceEndpoint = obtainNextEndpoint(connResponse, 'sources');
    //sourceReq is dinamically added from ZD object
    sourceReq.name = collectionName;
    sourceReq.sourceParameters.collection = collectionName;

    $.ajax({
        url: sourceEndpoint,
        type: 'post',
        data: JSON.stringify(sourceReq),
        headers: headers, // credentials are passed from ZD obj
        dataType: 'json',
        success: function (sourceResponse) {
             //$('#result').html('<div>' + JSON.stringify(sourceResponse) + ' </div>');
             $('#result').html('<p>The source has been created!</p>');
        },
        error: function (request, status, error) {
            message = request.responseText.message
            if(message.indexOf("doesn't exist") > -1){
                 $('#result').html('<p>Source created without a collection</p>');
            }
            else if(message.indexOf('already exists') > -1){
                 $('#result').html('<p>Source '+collection+' allready exists!</p>');
            }
            else{ alert(request.responseText);}
        }
    });
}

// handles HATEOAS response to obtain the next link
var obtainNextEndpoint = function(connResponse, linkName) {
    var result = null;
    var links = connResponse.links;
    links.forEach(function(link) {
      if (link.rel === linkName) {
        result = link.href;
      }
    });

    return result;
}

createSource()
