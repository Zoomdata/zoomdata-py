require(["ZoomdataSDK", "jquery"], function(ZoomdataSDK, jquery) {

    //Tools functions declared in js/tools.js
    //Variables declared in the caller function
    _INITIAL_VARS_

    var tmp_group = "" //To store the name of the group
    var filters = []
    var accessorMultiGroup = "Multi Group By"

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
    }).then(function(client) {
        window.client = client;
        return (client)
    }).then(function(client) {
        console.log("Requesting visualization...");
        client.visualize({
            "source": {
                "name": v_source
            },
            "visualization": "Line Trend: Attribute Values",
            "config": {
                "filters": v_filters,
                "tz": "UTC"
            },
            "variables": v_vars,
            "element": v_divLocation
        }).done(function(result) {
            window.viz = result;
            console.log("Thread:", window.viz);
            var accesorsKeys = getKeys(window.viz.dataAccessors);
            console.log("Accesors keys", accesorsKeys);

            //Selects
            var metricSel= $("#metric");
            var groupSel = $("#group");
            var trendSel= $("#trend-attr");
            var timeUnit = $("#time-unit")

            //Get the time granularities (MINUTE, DAY, WEEK...)
            grps = window.viz.dataAccessors[accessorMultiGroup].getGroups()
            $.each(grps, function(){ //Two groups are presented: Attribute and Time
                if(this.type == "TIME"){
                    v_trend = this
                    if(!inList(this.granularities, v_defPicker["unit"])){
                        v_defPicker["unit"] = this.func
                    }
                    else{ v_trend.func = v_defPicker["unit"]}
                    $.each(this.granularities, function(){ //Two groups are presented: Attribute and Time
                        if(v_defPicker["unit"] == this){
                            timeUnit.append($("<option />").val(this).text(this).attr("selected","selected"))
                        }
                        else{ timeUnit.append($("<option />").val(this).text(this)) }
                    });
                }
                else{v_group = this}
            })
            $.each(window.viz.source.objectFields, function() {
                //Get the fields
                filters.push(this);
                if (this.visible) {
                    if (this.type == "NUMBER" || this.type == "MONEY" || this.type == "INTEGER") {
                        if(v_defPicker["metric"] == this.name || v_defPicker["metric"] == this.label){
                           metricSel.append($("<option />").val(this.name).text(this.label).attr("selected","selected"));
                            v_metric = { func: this.func.toLowerCase(), 
                                        label:this.label, 
                                        name: this.name, 
                                        type: this.type }
                           }else{ metricSel.append($("<option />").val(this.name).text(this.label)) }
                    }//axis if
                    else if (this.type == "TIME") {
                        if (v_defPicker["trend"] == this.name || v_defPicker["trend"] == this.label) {
                            trendSel.append($("<option />").val(this.name).text(this.label).attr("selected", "selected"));
                            v_trend.name = this.name
                            v_trend.sort.name = this.name
                        } else {
                            trendSel.append($("<option />").val(this.name).text(this.label))
                        }
                    } else { //Atribute
                        if (v_defPicker["group"] == this.name || v_defPicker["group"] == this.label) {
                            groupSel.append($("<option />").val(this.name).text(this.label).attr("selected", "selected"));
                            v_group.name = this.name
                            v_group.sort.name = this.name
                        } else {
                            groupSel.append($("<option />").val(this.name).text(this.label))
                        }
                    }
                } //Every picker is filled the their respective options
            });
            //Set as selected the option matching the function
            op = v_defPicker.operation.toLowerCase()
            if (v_defPicker.operation != "") {
                opt = $("#func option[value=" + op + "]")
                opt.attr("selected", "selected")
            }
            // ------ Metric Checking -----------
            if (!$.isEmptyObject(v_metric)) {
                if (op != "") {
                    v_metric.func = op
                }
                window.viz["dataAccessors"]["Y Axis"].setMetric(v_metric)
            }
            // ------ Trend Checking -----------
            if (!$.isEmptyObject(v_trend) && v_defPicker["trend"] != "") {
                if (v_defPicker.unit != "none") {
                    v_trend.defaultGranularity = v_defPicker.unit
                    v_trend.func = v_defPicker.unit
                }
            }
            // ----- Group/Dimension Checking -----------
            if (!$.isEmptyObject(v_group) && v_defPicker["group"] != "") {
                if (!$.isEmptyObject(v_metric)) {
                    v_group.sort.name = v_metric.name
                    v_group.sort.metricFunc = v_metric.func
                }
            }
            v_group.limit = v_defPicker.limit;
            var accessor = window.viz["dataAccessors"][accessorMultiGroup];
            accessor.resetGroups([v_group, v_trend])

            $("#load-message").html("");
        }); //done
    }); //then

    $("#metric").change(function() {
        var name = $("#metric").val();
        var funct = $("#func").val();
        var f = getObj(name, filters)
        if (name == "count") { //If the metric is count, the operator must be hidden
            $("#func").hide();
            $("#op-span").hide();
        } else {
            v_metric = {
                func: f.func.toLowerCase(),
                label: f.label,
                name: f.name,
                type: f.type
            }
            $("#func").show();
            $("#op-span").show();
        }
        if (funct != "") {
            v_metric.func = funct;
        }
        console.group("Y AXIS")
        console.log(name);
        console.log(v_metric);
        console.groupEnd()
        v_metric.name = name;
        var accessor = window.viz["dataAccessors"]["Y Axis"];
        accessor.setMetric(v_metric)
    });

    $("#func").change(function() {
        var func = $("#func").val();
        if (func == "") {
            //If no operation, set the default operation of the metric
            var f = getObj(v_metric.name, filters)
            v_metric.func = f.func.toLowerCase()
        } else {
            v_metric.func = func;
        }
        console.group("Function")
        console.log(func);
        console.log("met", v_metric);
        console.groupEnd()
        var mAccessor = window.viz["dataAccessors"]["Y Axis"];
        mAccessor.setMetric(v_metric)
    });

    $("#group").change(function() {
            var name = $( "#group" ).val();
            var funct = $("#func").val();
            var f = getObj(name, filters)
            v_group.name = f.name
            if(!$.isEmptyObject(v_metric) && v_metric.name != "count"){
                v_group.sort.name = v_metric.name
                v_group.sort.metricFunc = v_metric.func
                if(funct != ""){
                    v_group.sort.metricFunc = funct 
                }
            }
            else{
                v_group.sort = {"name":"count","dir":"desc"}
            }
            console.group("Group By")
            console.log(name);
            console.log(v_group);
            console.groupEnd()
            var accessor = window.viz["dataAccessors"][accessorMultiGroup];
            accessor.resetGroups([v_group, v_trend]);
    });

    $("#trend-attr").change(function() {
        var name = $("#trend-attr").val();
        var timeUnit = $("#time-unit").val();
        if (timeUnit == "") {
            timeUnit = "DAY"
        }
        var f = getObj(name, filters)
        if (f.type == "TIME") { //is a dimension
            v_trend.name = f.name
            v_trend.limit = 1000
            v_trend.defaultGranularity = timeUnit
            v_trend.func = timeUnit
            v_trend.type = "TIME"
            v_trend.sort = {
                name: f.name,
                "dir": "asc"
            }
        }
        console.group("Group By")
        console.log(name);
        console.log(v_trend);
        console.groupEnd()
        var accessor = window.viz["dataAccessors"][accessorMultiGroup];
        accessor.resetGroups([v_group, v_trend]);
    });


    $("#time-unit").change(function() {
        var name = $("#time-unit").val();
        v_trend.func = name
        v_trend.defaultGranularity = name
        var accessor = window.viz["dataAccessors"][accessorMultiGroup];
        accessor.resetGroups([v_group, v_trend]);
    });

})
