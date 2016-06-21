require(["ZoomdataSDK", "jquery"], function(ZoomdataSDK, jquery) {

    //Tools functions declared in js/tools.js
    //Variables declared in the caller function
    _INITIAL_VARS_

    // Query configuration parameters
    var queryConfig = {
       tz: 'EST',
       player: null,
       fields: v_fields,
       //fields: [
          //{name:'pricepaid', limit: 1000},
          //{name:'catdesc'},
       //]
     }

      var queryData = undefined;
      var kernel = IPython.notebook.kernel
      $('#fetch'+v_logcount).html("Fetching the data, please wait ...")

      ZoomdataSDK.createClient({                      
            "credentials": {
                "key": v_credentials
            },
            "application": {
                "port": v_conf["port"],
                "path": v_conf["path"],
                "host": v_conf["host"],
                "secure": v_conf["secure"]
            }
        })
        // Create the query
        .then( function(client) {
            window.client = client;
            return( client.createQuery({name: v_source}, queryConfig) );
        })
        .then( function (result) {
          // Run the query and output the values
            return window.client.run(result);
        }).then( function(thread) {      
            thread.on('thread:message', function(data) {
                if (queryData === undefined) {
                  queryData = data;
                } 
                else {
                  queryData = data.reduce( function(coll,item){
                      coll.push( item );
                      return coll;
                  }, queryData );
                }
                
            }) // thread:message
            thread.on('thread:notDirtyData', function() {
                console.log('received ' + queryData.length + ' items')
                strdata = JSON.stringify(queryData)
                strdata = strdata.replace(/'/g,"--")
                strdata = strdata.replace(/null/g,"False")
                var command = "ZD._dframe = '"+strdata+"'";
                kernel.execute(command);
                console.log(queryData);
                var msg = "Data is ready, you may access it with ZD.get()";
                $('#done'+v_logcount).html(msg)
              })
             thread.on('thread:exeption', function(error) {
                console.log('exception: ', error);
                $('#done'+v_logcount).html(error)
          });
        }) //then
        .catch( function (error) {
          reject(error);
        })
})


