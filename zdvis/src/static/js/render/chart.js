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

    //Unit time selector
    granularities= ["MINUTE","HOUR","DAY","WEEK","MONTH","YEAR"]
    var timeOpt = ""
    for(g in granularities){
        timeOpt += buildHTML("option", granularities[g], {value:granularities[g]})
    }
    timeSelect = buildHTML("select", timeOpt , {id: "time", class:"pickers"})

    //This is to validate correct pickers field names/labels specified by the user in graph()
    var fieldNames  = []
    var fieldLabels = []

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

            //Fill and create the selectors with the source fields
            var dimOpt = buildHTML("option","Select attribute", {value:""})
            var metOpt = buildHTML("option","Select metric", {value:""})
                metOpt += buildHTML("option","Count", {value:"count"})
            var trendOpt = buildHTML("option","Select attribute ", {value:""})

            var multiMetricTable = []
            checkbox = buildHTML("input", "", {value: "count", type:"checkbox", id: "count", name:"multi-metrics"})
            label = buildHTML("label", "Count", {for: "count"})
            hidden = buildHTML("input", "", {data: "count", type:"hidden"}) //This is a hack for the setPickers function
            multiMetricTable.push([checkbox, label, hidden])

            $.each(window.viz.source.objectFields, function() {
                if (this.visible) {
                    fieldNames.push(this.name)
                    fieldLabels.push(this.label)
                    if (this.type == "NUMBER" || this.type == "MONEY" || this.type == "INTEGER") {
                        metOpt += buildHTML("option", this.label, {value: this.name})
                        //Multiple-metrics
                        checkbox = buildHTML("input", "", {value: this.name, type:"checkbox", id: this.name, name:"multi-metrics"})
                        label = buildHTML("label", this.label, {for: this.name})
                        funcSel = buildHTML("select", funcOpt, { id: this.name, class: "pickers" })
                        multiMetricTable.push([checkbox, label, funcSel])
                    } 
                    else if (this.type == "ATTRIBUTE") {
                        dimOpt += buildHTML("option", this.label, {value: this.name})
                    }
                    else if (this.type == "TIME") {
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
            if(v_showPickers){ //If the user wants to see the pickers
                pickers = ""
                for(acc in v_pickersValues){
                    id=acc.toLowerCase().replace(/ /g, "-")
                    text = acc
                    vals =  v_pickersValues[acc]
                    if(vals.type == "ATTRIBUTE" || vals.type == "TIME"){
                        text = acc +": <b>"+vals.field+"</b>"
                        if(vals.time != null) text += "<b>("+vals.time+")</b>"
                        pickers+= "<button id=\""+id+"\" class=\"btn-dimension btnp\" data-name=\""+acc+"\">"+text+"</button>"
                        pickers += "&nbsp;"
                    }
                    else{
                        if(vals.length == undefined){ 
                            text = acc + ": <b>" + vals.met + "</b>"
                            if (vals.func != null) text += "<b>(" + vals.func + ")</b>"
                            pickers += "<button id=\"" + id + "\" class=\"btn-metric btnp\" data-name=\"" + acc + "\">" + text + "</button>"
                            pickers += "&nbsp;"
                        }
                        else{ //A multi-metric chart
                            if(acc.indexOf("Color") == -1){ //Do not show Bar Color metric for Bars: Multiple Metrics
                                text = acc + ": <b>(" + vals.length.toString() + " selected)</b>"
                                if (vals.func != null) text += "<b>(" + vals.func + ")</b>"
                                pickers += "<button id=\"" + id + "\" class=\"btn-multi-metric btnp\" data-name=\"" + acc + "\">" + text + "</button>"
                                pickers += "&nbsp;"
                            }
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
                                                style:"width:90%;color:black"})
        var type = v_pickersValues[btnAccessor].type 
        if(type == "ATTRIBUTE"){
            table = [["Attribute",dimensionSelect],
                     ["Sort By", metricSelect],
                     ["Operator", funcSelect ], 
                     ["Order",sortSelect ],
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
                    time: time,
                    sort: sortby,
                    mfunc: metFunc,
                    dir: dir,
                    limit: parseInt(limit),
                    type: type
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
        table = [["Metric",metricSelect],["Operator", funcSelect ]]
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
            $("#func").prop("disabled", "disabled");
        }
        else{
            $("#func").prop("disabled", false);
        }
    })
})

