require(["ZoomdataSDK", "jquery"], function(ZoomdataSDK, jquery) {

    //Tools functions declared in js/tools.js
    //Variables declared in the caller function
    _INITIAL_VARS_

    var yaxis1 = {}
    var yaxis2 = {}
    var filters = []

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
            "visualization": "Line & Bars Trend",
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
            var yaxis1Sel = $("#yaxis1");
            var yaxis2Sel = $("#yaxis2");
            var trendSel= $("#trend-attr");
            $.each(window.viz.source.objectFields, function() {
                filters.push(this);
                if (this.visible) {
                    if (this.type == "NUMBER" || this.type == "MONEY" || this.type == "INTEGER") {
                        if(v_defPicker["yaxis1"] == this.name || v_defPicker["yaxis1"] == this.label){
                                   yaxis1Sel.append($("<option />").val(this.name)
                                                                       .text(this.label)
                                                                       .attr("selected","selected"));
                                    yaxis1= { func: this.func.toLowerCase(), 
                                                label:this.label, 
                                                name: this.name, 
                                                type: this.type }
                           }
                           else{ yaxis1Sel.append($("<option />").val(this.name).text(this.label)) }

                        if(v_defPicker["yaxis2"] == this.name || v_defPicker["yaxis2"] == this.label){
                                   yaxis2Sel.append($("<option />").val(this.name)
                                                                       .text(this.label)
                                                                       .attr("selected","selected"));
                                    yaxis2 = { func: this.func.toLowerCase(), 
                                                label:this.label, 
                                                name: this.name, 
                                                type: this.type }

                        }
                       else{ yaxis2Sel.append($("<option />").val(this.name).text(this.label)) }

                }else if (this.type == "TIME") {
                        if(v_defPicker["trend"] == this.name || v_defPicker["trend"] == this.label){
                                   trendSel.append($("<option />").val(this.name)
                                                                       .text(this.label)
                                                                       .attr("selected","selected"));
                            
                        }
                        else{
                            trendSel.append($("<option />").val(this.name).text(this.label))
                        }
                    }
                } 
            });
              //Set as selected the option matching the function
                op1 = v_defPicker.operation1.toLowerCase()
                if(v_defPicker.operation1 != ""){
                    opt = $("#func1 option[value="+op1+"]")
                    opt.attr("selected","selected")
                    console.log(opt)
                }
                op2 = v_defPicker.operation2.toLowerCase()
                if(v_defPicker.operation2 != ""){
                    opt = $("#func2 option[value="+op2+"]")
                    opt.attr("selected","selected")
                    console.log(opt)
                }
              if(!$.isEmptyObject(yaxis1)){
                  if(op1 != ""){ yaxis1.func = op1 }
                   window.viz["dataAccessors"]["Y1 Axis"].setMetric(yaxis1)
              }
              if(!$.isEmptyObject(yaxis2)){
                  if(op2 != ""){ yaxis2.func = op2 }
                   window.viz["dataAccessors"]["Y2 Axis"].setMetric(yaxis2)
              }
            $("#load-message").html("");
        });
    });

    $("#yaxis1").change(function() {
        var name = $("#yaxis1").val();
        var funct = $("#func1").val();
        var f = getObj(name, filters)
        yaxis1 = { func: f.func.toLowerCase(),
                   label: f.label,
                   name: f.name,
                   type: f.type }
        if (funct != "") { yaxis1.func = funct;}
        if (name == "count") { //If the metric is count, the operator must be hidden
            $("#func1").hide();
            $("#op-span1").hide();
        } else {
            $("#func1").show();
            $("#op-span1").show();
        }
        console.group("Y1 AXIS")
        console.log(name);
        console.log(yaxis1);
        console.groupEnd()
        yaxis1.name = name;
        var accessor = window.viz["dataAccessors"]["Y1 Axis"];
        accessor.setMetric(yaxis1)
    });

    $("#func1").change(function() {
        var func = $("#func1").val();
        if (func == "") {
            //If no operation, set the default operation of the metric
            var f = getObj(yaxis1.name, filters)
            yaxis1.func = f.func.toLowerCase()
        } else {
            yaxis1.func = func;
        }
        console.group("Function 1")
        console.log(func);
        console.log("met", yaxis1);
        console.groupEnd()
        var mAccessor = window.viz["dataAccessors"]["Y1 Axis"];
        mAccessor.setMetric(yaxis1)
    });

    $("#yaxis2").change(function() {
        var name = $("#yaxis2").val();
        var funct = $("#func2").val();
        var f = getObj(name, filters)
        yaxis2 = { func: f.func.toLowerCase(),
                   label: f.label,
                   name: f.name,
                   type: f.type }
        if (funct != "") { yaxis2.func = funct;}
        if (name == "count") { //If the metric is count, the operator must be hidden
            $("#func2").hide();
            $("#op-span2").hide();
        } else {
            $("#func2").show();
            $("#op-span2").show();
        }
        console.group("Y2 AXIS")
        console.log(name);
        console.log(yaxis2);
        console.groupEnd()
        yaxis2.name = name;
        var accessor = window.viz["dataAccessors"]["Y2 Axis"];
        accessor.setMetric(yaxis2)
    });

    $("#func2").change(function() {
        var func = $("#func2").val();
        if (func == "") {
            //If no operation, set the default operation of the metric
            var f = getObj(yaxis2.name, filters)
            yaxis2.func = f.func.toLowerCase()
        } else {
            yaxis2.func = func;
        }
        console.group("Function 2")
        console.log(func);
        console.log("met", yaxis2);
        console.groupEnd()
        var mAccessor = window.viz["dataAccessors"]["Y2 Axis"];
        mAccessor.setMetric(yaxis2)
    });

    $("#trend-attr").change(function() {
            var name = $( "#group" ).val();
            var f = getObj(name, filters)
            if(f.type == "TIME"){ //is a dimension
                v_group.name = f.name
                if(metric.name != "count"){
                    v_group.sort.name = v_metric.name
                    v_group.sort.metricFunc = v_metric.func
                    if(funct != ""){
                        v_group.sort.metricFunc = funct 
                    }
                }
                else{
                    v_group.sort = {"name":"count","dir":"desc"}
                }
            }
            console.group("Group By")
            console.log(name);
            console.log("Accessor:", v_groupAccessor);
            console.log(group);
            console.groupEnd()
            list = ["Donut","Packed","Scatter","Pie","Tree","Word"]
            var accessor = window.viz["dataAccessors"][v_groupAccessor];
            if(inList(list, v_chart)){
                accessor.setGroup(v_group)
            }
            else{
                accessor.resetGroups([v_group]);
            }
    });

})
