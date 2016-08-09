require.config({
    paths: {
        "jquery": "https://ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min",
        "ZoomdataSDK": "https://pubsdk.zoomdata.com:8443/zoomdata/sdk/2.0/zoomdata-client.min",
        "jQueryConfirm": "https://cdnjs.cloudflare.com/ajax/libs/jquery-confirm/2.5.1/jquery-confirm.min",
        "bootstrap": "https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/js/bootstrap.min"
    },
   shim:{
       "jQueryConfirm":{
           deps:["jquery"]
       },
       "bootstrap":{
           deps:["jquery"]
       }
   }
});
require(["ZoomdataSDK", "jquery","jQueryConfirm", "bootstrap"], function(ZoomdataSDK, jquery, jQueryConfirm, bootstrap) {
    //Tools functions declared in js/tools.js
    //Variables declared in the caller function
    _INITIAL_VARS_

    //Main selectors
    var dimensionSelect = ""
    var trendSelect = ""
    var metricSelect = ""

    //The label for the volume may change
    var volumeLabel= "Count"

    //Operation for Metric selectors
    funcs = ["Sum","Avg","Min","Max"]
    var funcOpt = ""
    for(op in funcs){
        funcOpt += buildHTML("option", funcs[op], {value: funcs[op].toLowerCase()})
    }
    var funcSelect = buildHTML("select", funcOpt, {id: "func", class:"pickers"})

    //Sort direction selector
    sortOpt = buildHTML("option", "ASC", {value: "asc"})
    sortOpt += buildHTML("option", "DESC", {value: "desc"})
    var sortSelect = buildHTML("select", sortOpt , {id: "sort", class:"pickers"})

    //Chronological and reverse chronological order  for time attributes (trend charts)
    cronOpt= buildHTML("option", "Chronological", {value: "asc"})
    cronOpt += buildHTML("option", "Reverse chronological", {value: "desc"})
    var cronSelect = buildHTML("select", cronOpt , {id: "sort", class:"pickers"})

    //Bars settings for histogram chart
    barsOpt = buildHTML("option", "Auto", {value: "histogram"})
    barsOpt += buildHTML("option", "Limit to", {value: "histogram_by_count"})
    barsOpt += buildHTML("option", "Interval", {value: "histogram_by_size"})
    var barsSelect  = buildHTML("select", barsOpt, {id: "func", class:"pickers"})

    //Unit time selector
    granularities= ["MINUTE","HOUR","DAY","WEEK","MONTH","YEAR"]
    var timeOpt = ""
    for(g in granularities){
        timeOpt += buildHTML("option", granularities[g], {value:granularities[g]})
    }
    timeSelect = buildHTML("select", timeOpt , {id: "time", class:"pickers"})

    //This is to validate correct pickers field names/labels specified by the user in graph()
    var metricFields = {fields:[], labels:[]}
    var dimensionFields = {fields:[], labels:[]}

    //Start the visualization
    ZoomdataSDK.createClient({
        "credentials": v_credentials,
        "application": {
            "port": v_conf["port"],
            "path": v_conf["path"],
            "host": v_conf["host"],
            "secure": v_conf["secure"]
        }
    }).then(function(client) {
        window.client = client;
        return (client)
    }).then(function(client) {
        console.log("Requesting visualization...");
        client.visualize({
            "source": {
                "name": v_source
            },
            "visualization": v_chart,
            "config": {
                "filters": v_filters,
                "time": v_time,
                "tz": "UTC"
            },
            "variables": v_vars,
            "element": v_divLocation
        }).done(function(result) {
            window.viz = result;
            console.log("Result",result);

            //Set the colors if specified
            for(acc in v_colors){
                window.viz.dataAccessors[acc].setColorSet(v_colors[acc])
            }

            //Get the correct label for the volume
            volumeLabel = window.viz.source.volumeMetric.label

            //Fill and create the selectors with the source fields
            var dimOpt = buildHTML("option","Select attribute", {value:""})
            var metOpt = buildHTML("option","Select metric", {value:""})
                metOpt += buildHTML("option", volumeLabel, {value:"count"})
            var trendOpt = buildHTML("option","Select attribute ", {value:""})

            var multiMetricTable = []
            checkbox = buildHTML("input", "", {value: "count", type:"checkbox", id: "count", name:"multi-metrics"})
            label = buildHTML("label", volumeLabel, {for: "count"})
            hidden = buildHTML("input", "", {data: "count", type:"hidden"}) //This is a hack for the setPickers function
            multiMetricTable.push([checkbox, label, hidden])

            $.each(window.viz.source.objectFields, function() {
                if (this.visible) {
                    if (this.type == "NUMBER" || this.type == "MONEY" || this.type == "INTEGER") {
                        //Save the metric field and label
                        metricFields.fields.push(this.name)
                        metricFields.labels.push(this.label)
                        //Create the select
                        metOpt += buildHTML("option", this.label, {value: this.name})
                        //Multiple-metrics
                        checkbox = buildHTML("input", "", {value: this.name, type:"checkbox", id: this.name, name:"multi-metrics"})
                        label = buildHTML("label", this.label, {for: this.name})
                        funcSel = buildHTML("select", funcOpt, { id: this.name, class: "pickers" })
                        multiMetricTable.push([checkbox, label, funcSel])
                    } 
                    else if (this.type == "ATTRIBUTE") {
                        dimensionFields.fields.push(this.name)
                        dimensionFields.labels.push(this.label)
                        dimOpt += buildHTML("option", this.label, {value: this.name})
                    }
                    else if (this.type == "TIME") {
                        dimensionFields.fields.push(this.name)
                        dimensionFields.labels.push(this.label)
                        trendOpt += buildHTML("option", this.label, {value: this.name})
                    }
                }
            });
            dimensionSelect = buildHTML("select", dimOpt, {id: "dimension", class:"pickers"})
            trendSelect  = buildHTML("select", trendOpt, {id: "dimension", class:"pickers"})
            metricSelect = buildHTML("select", metOpt, {id: "metric", class:"pickers"})
            multiMetric = buildHTML("div", makeTable(multiMetricTable, {class:"multi"}), { id: "multimetric", class:"multimetric" })

            //Load the values that comes from the visualization definition
            v_pickersValues = loadDefinitionPickers() 

            //Set the pickers specified by the user (if any) in graph()
            if(v_defPicker) loadUserPickers()
            console.log("Pickers",v_pickersValues)
            
            //Set the dimension & metric pickers buttons in the DOM
            if (v_showPickers) { //If the user wants to see the pickers
                pickers = ""
                for (acc in v_pickersValues) {
                    id = acc.toLowerCase().replace(/ /g, "-")
                    text = acc
                    vals = v_pickersValues[acc]
                    if (vals.type == "ATTRIBUTE" || vals.type == "TIME") {
                        text = acc + ": <b>" + vals.field + "</b>"
                        if (vals.func != null && !v_isHistogram) text += "<b>(" + vals.func + ")</b>"
                        pickers += "<button id=\"" + id + "\" class=\"btn-dimension btnp\" data-name=\"" + acc + "\">" + text + "</button>"
                        pickers += "&nbsp;"
                    } else {
                        if (!v_isHistogram){
                            if (vals.length == undefined) {
                                text = acc + ": <b>" + vals.met + "</b>"
                                if (vals.func != null) text += "<b>(" + vals.func + ")</b>"
                                pickers += "<button id=\"" + id + "\" class=\"btn-metric btnp\" data-name=\"" + acc + "\">" + text + "</button>"
                                pickers += "&nbsp;"
                            } else { //A multi-metric chart
                                if (acc.indexOf("Color") == -1) { //Do not show Bar Color metric for Bars: Multiple Metrics
                                    text = acc + ": <b>(" + vals.length.toString() + " selected)</b>"
                                    if (vals.func != null) text += "<b>(" + vals.func + ")</b>"
                                    pickers += "<button id=\"" + id + "\" class=\"btn-multi-metric btnp\" data-name=\"" + acc + "\">" + text + "</button>"
                                    pickers += "&nbsp;"
                                }
                            }
                        }
                        else{ //A histogram bar
                                text = "Histogram: <b>" + vals.field + "</b>"
                                pickers += "<button id=\"" + id + "\" class=\"btn-histogram btnp\" data-name=\"" + acc + "\">" + text + "</button>"
                                pickers += "&nbsp;"
                        }

                    }
                }
                $("div#pickers").html(pickers)
            }

            //Remove the loading message
            $("#load-message").html("");

        }); //done 
    }); //then

    //Dimension Handler
    $("body").on("click", "button.btn-dimension", function () {
        var btn = $(this)
        var btnAccessor = btn.attr("data-name")
        var limitInput = buildHTML("input","",{ id:"limit", 
                                                value: v_pickersValues[btnAccessor].limit, 
                                                class:"value-input"})
        var type = v_pickersValues[btnAccessor].type 

        //Place in the sort by select, the selected dimension
        dim = v_pickersValues[btnAccessor].field
        label = dimensionFields.labels[dimensionFields.fields.indexOf(dim)]
        find = "</option></select>"
        selDimOpt = buildHTML("option", label , { value: dim })
        selDimOpt = "</option>" + selDimOpt + "</select>"
        var newMetricSelect = metricSelect.replace(find, selDimOpt)
        var newFuncSelect = funcSelect
        var newSortSelect = sortSelect 

        //Set the func select as disabled and the label to alphabetical if sort = field
        if(dim == v_pickersValues[btnAccessor].sort){
            find = "id= \"func\""
            rep = find + " disabled"
            newFuncSelect = funcSelect.replace(find, rep)
            newSortSelect = sortSelect.replace("ASC", "Alphabetical")
            newSortSelect = newSortSelect.replace("DESC", "Reverse alphabetical")
        }
        //Set the func select as disabled if sort is count
        if(v_pickersValues[btnAccessor].sort == "count"){
            find = "id= \"func\""
            rep = find + " disabled"
            newFuncSelect = funcSelect.replace(find, rep)
        }

        if(type == "ATTRIBUTE"){
            table = [["Attribute",dimensionSelect],
                     ["Sort By", newMetricSelect],
                     ["Operator", newFuncSelect ], 
                     ["Order",newSortSelect ],
                     ["Limit", limitInput]] 
        }
        else{ //TIME
            table = [["Time Attribute",trendSelect], 
                     ["Granularity", timeSelect], 
                     ["Order", cronSelect], 
                     ["Limit", limitInput]] 
        }
        var content = makeTable(table,{class:"pickers"})
        //Load the selectors with the last used values
        content = setPickers(content ,v_pickersValues[btnAccessor])
        $.confirm({
            title: btnAccessor,
            theme: "black",
            confirmButton: "Apply",
            confirmButtonClass: "btn-success",
            content: content,
            confirm: function () {
                var field = this.$b.find("#dimension").val()
                var time = this.$b.find("#time").val()
                var sortby = this.$b.find("#metric").val()
                var metFunc = this.$b.find("#func").val()
                var dir = this.$b.find("#sort").val()
                var limit = this.$b.find("#limit").val()
                //Save the values
                v_pickersValues[btnAccessor] = {
                    field: field,
                    func: time,
                    sort: sortby,
                    mfunc: metFunc,
                    dir: dir,
                    limit: parseInt(limit),
                    type: type
                }
                //If selected sortby is the attribute, func must be null
                if(metricFields.fields.indexOf(sortby) == -1){
                    v_pickersValues[btnAccessor].mfunc = undefined
                }
                //Set the dimension
                setDimension(btnAccessor)
                //Update the button text with the selected dimension
                fieldLabel = btnAccessor + ": <b>"+field+"</b>"
                if(type == "TIME") { 
                    fieldLabel += "<b>("+time+")</b>"
                }
                btn.html(fieldLabel)
            }
        })
    })

    //Metric Handler
    $("body").on("click","button.btn-metric", function() {
        var btn = $(this)
        var btnAccessor = btn.attr("data-name")
        var newFuncSelect = funcSelect
        //Set the func select as disabled if sort is count
        if(v_pickersValues[btnAccessor].met == "count"){
            find = "id= \"func\""
            rep = find + " disabled"
            newFuncSelect = funcSelect.replace(find, rep)
        }
        table = [["Metric",metricSelect],["Operator", newFuncSelect ]]
        //var content = multiMetric
        var content = makeTable(table,{class: "pickers"})
        var type = v_pickersValues[btnAccessor].type 
        content = setPickers(content ,v_pickersValues[btnAccessor])
        $.confirm({
            title: btnAccessor,
            theme: "black",
            confirmButtonClass: "btn-success",
            confirmButton: "Apply",
            content: content,
            confirm: function () {
                var met = this.$b.find("#metric").val()
                var metLabel = this.$b.find("#metric option:selected").text()
                var func = this.$b.find("#func").val()
                func = (met == "count") ? "" : func
                //Save the values
                v_pickersValues[btnAccessor] = {
                    met: met,
                    func: func,
                    type: type
                }
                //Set the metric
                setMetric(btnAccessor)
                //Update the button text with the selected metric
                metLabel = btnAccessor+": <b>"+met+"</b>"
                if(func != ""){
                    metLabel += "<b>("+func+")</b>" 
                }
                btn.html(metLabel)
            }
        })
    })

    //Histogram Handler
    $("body").on("click","button.btn-histogram", function() {
        var btn = $(this)
        var btnAccessor = btn.attr("data-name")
        var argsInput = buildHTML("input","",{ id:"args", 
                                                value: v_pickersValues[btnAccessor].args, 
                                                class:"value-input"})
        //Set the args input as disabled if sort is count
        if(v_pickersValues[btnAccessor].func == "$histogram"){
            find = "value-input\""
            rep = "value-input disabled\" disabled=\"disabled\""
            argsInput = argsInput.replace(find, rep)
            argsInput = argsInput.replace("undefined", "0")
        }
        table = [["Attribute",metricSelect],["Bars Settings", barsSelect],["Bars", argsInput]]
        var content = makeTable(table,{class: "pickers"})
        var type = v_pickersValues[btnAccessor].type 
        content = setPickers(content ,v_pickersValues[btnAccessor])
        $.confirm({
            title: "Histogram Settings",
            theme: "black",
            confirmButtonClass: "btn-success",
            confirmButton: "Apply",
            content: content,
            confirm: function () {
                var field = this.$b.find("#metric").val()
                var histgrm = "$"+this.$b.find("#func").val()
                var fieldLabel= this.$b.find("#metric option:selected").text()
                var args = this.$b.find("#args").val()
                //Save the values
                    v_pickersValues[btnAccessor] = {
                        field: field,
                        sort: field,
                        func: histgrm,
                        mfunc: undefined,
                        label: fieldLabel,
                        args: parseInt(args),
                        dir: "desc",
                        limit: 10000,
                        type: type
                    }

                //Set the metric
                setDimension(btnAccessor)
                //Update the button text with the selected metric
                label = "Histogram: <b>"+field+"</b>"
                btn.html(label)

            }
        })
    })

    //Multi-Metric Handler
    $("body").on("click", "button.btn-multi-metric", function() {
        var btn = $(this)
        var btnAccessor = btn.attr("data-name")
        content = multiMetric
        content = setPickers(content ,v_pickersValues[btnAccessor])
        $.confirm({
            title: btnAccessor,
            theme: "black",
            confirmButtonClass: "btn-success",
            confirmButton: "Apply",
            content: content,
            confirm: function() {
                values = []
                $("input[name=\"multi-metrics\"]:checked").each(function() {
                   values.push(this.value); 
                });
                console.log(values)
                v_pickersValues[btnAccessor] = []
                for(pos in values){
                    v = values[pos]
                    v_pickersValues[btnAccessor].push({
                        met: v,
                        label: this.$b.find("label[for=\""+v+"\"]").text(),
                        func: this.$b.find("select#"+v).val()
                    })
                }
                console.log(v_pickersValues)
                //Set the metric
                setMetric(btnAccessor)
                //Update the button text with amount of selected metrics
                metLabel = btnAccessor+": <b>("+values.length.toString()+" selected)</b>"
                btn.html(metLabel)
            }
        })
    })

    //Disable the operation selector if users selects "count"
    $("body").on("change", "select#metric", function(){
        met = $("select#metric").val();
        if(met == "count"){
            $("select#func").prop("disabled", "disabled");
        }
        else{
            $("select#func").prop("disabled", false);
        }
    })

    //Disable the value input if bars setting for histogram is auto
    $("body").on("change", "select#func", function(){
        setting = $("select#func").val();
        if(setting == "histogram"){
            $("#args").prop("disabled", true);
            $("#args").addClass("disabled");
        }
        else{
            $("#args").prop("disabled", false);
            $("#args").removeClass("disabled");
        }
    })

    //Append dimension to metric to allow alphabetical sorting
    $("body").on("change", "select#dimension", function() {
       if($("select#metric option").length != metricFields.fields.length ){
          $("select#metric").find("option:last").remove();
       }
       $("select#metric").append($("<option>", {
          value: $( "select#dimension option:selected" ).val(),
          text: $( "select#dimension option:selected" ).text(),
       }));
       if($("select#dimension option:selected").text() != $( "select#metric option:selected" ).text()){
          $("select#func").prop("disabled", false);
       }
   })

    $("body").on("change", "select#metric", function() {
       if($("select#dimension option:selected").text() == $( "select#metric option:selected" ).text()){
          $("select#func").prop("disabled", "disabled");
          $("select#sort option:contains(\"ASC\")").text("Alphabetical");
          $("select#sort option:contains(\"DESC\")").text("Reverse alphabetical");
       }
       else{
          $("select#func").prop("disabled", false);
          $("select#sort option:contains(\"Alphabetical\")").text("ASC");
          $("select#sort option:contains(\"Reverse alphabetical\")").text("DESC");
       }
    })
})

