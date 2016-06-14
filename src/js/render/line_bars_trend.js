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
            var timeUnit = $("#time-unit")
            //Get the time granularities (MINUTE, DAY, WEEK...)
            grp = window.viz.dataAccessors["Trend Attribute"].getGroup()
            $.each(grp.granularities, function(){
                if(v_defPicker["unit"] == this){
                    timeUnit.append($("<option />").val(this).text(this).attr("selected","selected"))
                }
                else{ timeUnit.append($("<option />").val(this).text(this)) }
            })
            $.each(window.viz.source.objectFields, function() {
                //Get the fields
                filters.push(this);
                if (this.visible) {
                    if (this.type == "NUMBER" || this.type == "MONEY" || this.type == "INTEGER") {
                        if(v_defPicker["yaxis1"] == this.name || v_defPicker["yaxis1"] == this.label){
                           yaxis1Sel.append($("<option />").val(this.name).text(this.label).attr("selected","selected"));
                            yaxis1= { func: this.func.toLowerCase(), 
                                        label:this.label, 
                                        name: this.name, 
                                        type: this.type }
                           }else{ yaxis1Sel.append($("<option />").val(this.name).text(this.label)) }

                        if(v_defPicker["yaxis2"] == this.name || v_defPicker["yaxis2"] == this.label){
                           yaxis2Sel.append($("<option />").val(this.name).text(this.label).attr("selected","selected"));
                            yaxis2 = { func: this.func.toLowerCase(), 
                                        label:this.label, 
                                        name: this.name, 
                                        type: this.type }
                         }else{ yaxis2Sel.append($("<option />").val(this.name).text(this.label)) }
                    }//axis if
                    else if (this.type == "TIME") {
                        if(v_defPicker["trend"] == this.name || v_defPicker["trend"] == this.label){
                           trendSel.append($("<option />").val(this.name).text(this.label).attr("selected","selected"));
                            v_group.name = this.name
                            v_group.defaultGranularity = this.defaultGranularity
                            v_group.func= this.defaultGranularity
                            v_group.type = "TIME"
                            v_group.sort = { name: this.name, "dir": "asc" }
                        }else{ trendSel.append($("<option />").val(this.name).text(this.label))}
                    }
                }//if is visible
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
              v_group.limit = v_defPicker.limit;
              if(!$.isEmptyObject(v_group)){
                  if(v_defPicker.unit != ""){
                        v_group.defaultGranularity = v_defPicker.unit
                        v_group.func= v_defPicker.unit
                  }
                window.viz["dataAccessors"]["Trend Attribute"].resetGroup(v_group);
              }

            $("#load-message").html("");
        }); //done
    }); //then

    $("#yaxis1").change(function() {
        var name = $("#yaxis1").val();
        var funct = $("#func1").val();
        var f = getObj(name, filters)
        if (name == "count") { //If the metric is count, the operator must be hidden
            $("#func1").hide();
            $("#op-span1").hide();
        } 
        else {
            yaxis1 = { func: f.func.toLowerCase(),
                       label: f.label,
                       name: f.name,
                       type: f.type }
            $("#func1").show();
            $("#op-span1").show();
        }
        if (funct != "") { yaxis1.func = funct;}
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
        if (name == "count") { //If the metric is count, the operator must be hidden
            $("#func2").hide();
            $("#op-span2").hide();
        } else {
            yaxis2 = { func: f.func.toLowerCase(),
                   label: f.label,
                   name: f.name,
                   type: f.type }
            $("#func2").show();
            $("#op-span2").show();
        }
        if (funct != "") { yaxis2.func = funct;}
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
        var name = $("#trend-attr").val();
        var timeUnit = $("#time-unit").val();
        if(timeUnit == ""){ timeUnit = "DAY" }
        var f = getObj(name, filters)
        console.log(f)
        if (f.type == "TIME") { //is a dimension
            v_group.name = f.name
            v_group.limit = 1000
            v_group.defaultGranularity = timeUnit
            v_group.func= timeUnit
            v_group.type = "TIME"
            v_group.sort = {
                name: f.name,
                "dir": "asc"
                }
            }
        console.group("Group By")
        console.log(name);
        console.log(v_group);
        console.groupEnd()
        var accessor = window.viz["dataAccessors"]["Trend Attribute"];
        //accessor.setGroup(v_group)
        accessor.resetGroup(v_group);
    });


    $("#time-unit").change(function() {
        var name = $("#time-unit").val();
        v_group.func = name
        v_group.defaultGranularity = name
        var accessor = window.viz["dataAccessors"]["Trend Attribute"];
        accessor.resetGroup(v_group);
    });

})
