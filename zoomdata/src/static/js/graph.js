/*
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 **/
require.config({
    paths: {
        "jquery": "https://ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min",
        "ZoomdataSDK": "https://sdk.zoomdata.com:8443/zoomdata/sdk/zoomdata-client.min",
        "jQueryConfirm": "https://cdnjs.cloudflare.com/ajax/libs/jquery-confirm/2.5.1/jquery-confirm.min",
        "lodash":"https://cdn.jsdelivr.net/lodash/4.14.1/lodash.min",
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
require(["ZoomdataSDK", "jquery","jQueryConfirm", "lodash", "bootstrap"], function(ZoomdataSDK, jquery, jQueryConfirm, lodash, bootstrap) {
    //Functions
    __FUNCTIONS__

    //Initial variables declaration
    __VARIABLES__

    //Main selectors
    var dimensionSelect = ""
    var trendSelect = ""
    var metricSelect = ""

    var dimOpt = buildHTML("option","Select attribute", {value:""})
    var metOpt = buildHTML("option","Select metric", {value:""})
    var trendOpt = buildHTML("option","Select attribute ", {value:""})

    //The label for the volume may change
    var volumeLabel= "Count"

    //Store the elements to build up the table in multi metrics pickers
    var multiMetricTable = []

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
    var metricFields = {fields:[], labels:[], types:[]}
    var dimensionFields = {fields:[], labels:[], types:[]}
    var fusionFields = false

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

            //Fill the first values for the multimetric table
            checkbox = buildHTML("input", "", {value: "count", type:"checkbox", id: "count", name:"multi-metrics"})
            label = buildHTML("label", volumeLabel, {for: "count"})
            hidden = buildHTML("input", "", {data: "count", type:"hidden"}) //This is a hack for the setPickers function
            multiMetricTable.push([checkbox, label, hidden])

            //Get the source fields and group them by type
            var types = {"ATTRIBUTE":[], "TIME":[], "INTEGER":[], "NUMBER":[], "MONEY":[]}
            $.each(window.viz.source.objectFields, function() {
                if (this.visible) {
                    types[this.type].push(this)
                }
            });

            //Populate the pickers
            for(type in types){
                if(types[type].length > 0){
                    if(metricTypes.indexOf(type) > -1){
                        metOpt += buildHTML("option", "[=="+type+"==]", {value: ""})
                    }
                    else{
                        dimOpt += buildHTML("option", "[=="+type+"==]", {value: ""})
                    }
                }
                organizePickers(types[type],type)
                if(type == "NUMBER"){
                    //Add the volume to the NUMBER section in the selector
                    metOpt += buildHTML("option", volumeLabel, {value:"count"})
                }
            }
            
            //Check for fusion sources and get the fused attributes
            fusedAttrs = window.viz.source.fusedAttributes
            if(fusedAttrs.length > 0){
                forms = function(c){
                    fields = _.map(c.forms, "form")
                    labels = _.map(c.forms, "label")
                    return {name:c.name, label: c.label, fields: fields, labels: labels}
                }
                fusionFields = _.map(fusedAttrs, forms)

                //Add the fusion fields to the picker 
                dimOpt += buildHTML("option", "[==FUSED ATTRS==]", {value: ""})
                _.map(fusionFields,function(f){
                    for(i in f.fields){
                        dimOpt += buildHTML("option", f.label+":"+f.labels[i], {value: f.fields[i]})
                    }
                })
            }

            //Check for calc (formulas) fields
            var hasCalc = false
            $.each(window.viz.source.formulas, function() {
                if(!hasCalc){
                    metOpt += buildHTML("option", "[==FORMULAS==]", {value: ""})
                    hasCalc = true
                }
                //Save the metric field and label
                metricFields.fields.push(this.name)
                metricFields.labels.push(this.label)
                metricFields.types.push("CALC")
                //Create the select
                metOpt += buildHTML("option", this.label, {value: this.name})
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
                        label = dimensionFields.labels[dimensionFields.fields.indexOf(vals.name)]
                        //If no attr label found is a fusion source
                        if(label == undefined) label = getFusionLabel(vals.form)
                        text = acc + ": <b>" + label + "</b>"
                        if (vals.func != null && !v_isHistogram) text += "<b> (" + vals.func + ")</b>"
                        pickers += "<button id=\"" + id + "\" class=\"btn-dimension btnp\" data-name=\"" + acc + "\">" + text + "</button>"
                        pickers += "&nbsp;"
                    } else {
                        label = (vals.name == "count") ? volumeLabel : metricFields.labels[metricFields.fields.indexOf(vals.name)]
                        if (!v_isHistogram){
                            if (vals.length == undefined) {
                                text = acc + ": <b>" + label + "</b>"
                                if (vals.func != null) text += "<b> (" + vals.func + ")</b>"
                                pickers += "<button id=\"" + id + "\" class=\"btn-metric btnp\" data-name=\"" + acc + "\">" + text + "</button>"
                                pickers += "&nbsp;"
                            } else { //A multi-metric chart
                                if (acc.indexOf("Color") == -1) { //Do not show Bar Color metric for Bars: Multiple Metrics
                                    text = acc + ": <b> (" + vals.length.toString() + " selected)</b>"
                                    if (vals.func != null) text += "<b> (" + vals.func + ")</b>"
                                    pickers += "<button id=\"" + id + "\" class=\"btn-multi-metric btnp\" data-name=\"" + acc + "\">" + text + "</button>"
                                    pickers += "&nbsp;"
                                }
                            }
                        }
                        else{ //A histogram bar
                                label = metricFields.labels[metricFields.fields.indexOf(vals.name)]
                                text = "Histogram: <b>" + label + "</b>"
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

    //Pickers handlers
    __PICKERS__

})

