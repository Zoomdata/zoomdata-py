require(["ZoomdataSDK", "jquery"], function(ZoomdataSDK, jquery) {

    //Tools functions declared in js/tools.js
    //Variables declared in the caller function
    _INITIAL_VARS_

    filters = []
    var tmp_group = "" //To store the name of the group
    var list = ["Donut","Packed","Scatter","Pie","Tree","Word"]

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
            "visualization": v_chart,
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
                  var metricFlag = false;
                  accesorsKeys.forEach(function(k) {
                        if (k.indexOf("roup") > -1) {
                            v_groupAccessor = k;
                        } else { //Metric, Size and Colors are metrics
                            if (!metricFlag) { 
                                v_metricAccessor = k;
                                metricFlag = true;
                            }
                            //When metricFlag is true, it means that a metric is setted as accessor
                            if (k.indexOf("etric") > -1) {
                                v_metricAccessor = k;
                            }
                        }
                   });
                  var metricSelect = $("#metric");
                  var dimensionSelect = $("#group");
                  $.each(window.viz.source.objectFields, function() {
                      filters.push(this);
                      if(this.visible){
                          if(this.type == "NUMBER" || this.type == "MONEY" || this.type == "INTEGER"){
                               if(v_defPicker["metric"] == this.name || v_defPicker["metric"] == this.label){
                                   metricSelect.append($("<option />").val(this.name)
                                                                       .text(this.label)
                                                                       .attr("selected","selected"));
                                    v_metric = { func: this.func.toLowerCase(), 
                                                label:this.label, 
                                                name: this.name, 
                                                type: this.type }
                               }
                               else{
                                   if(v_defPicker["metric"] == "count"){
                                       metricSelect.val("count");
                                   }
                                   metricSelect.append($("<option />").val(this.name).text(this.label));
                               }
                          }
                          else if(this.type == "ATTRIBUTE") { 
                               if(v_defPicker.dimension == this.name || v_defPicker.dimension == this.label){
                                   dimensionSelect.append($("<option />").val(this.name)
                                                                       .text(this.label)
                                                                       .attr("selected","selected"));
                                    tmp_group = this.name
                               }
                               else{
                                   dimensionSelect.append($("<option />").val(this.name).text(this.label)) 
                               }
                          }
                      }
                  });
                  //Set as selected the option matching the function
                    op = v_defPicker.operation.toLowerCase()
                    if(v_defPicker.operation != ""){
                        opt = $("#func option[value="+op+"]")
                        opt.attr("selected","selected")
                        console.log(opt)
                    }

                  //Set the default pickers in case they have been specified
                  //but as the group depends on the metric, and it can be setted with before the metric 
                  //check for last time if a metric was setted
                  v_group.limit = v_defPicker.limit;
                  if(!$.isEmptyObject(v_metric)){
                      if(op != ""){ v_metric.func = op }
                       window.viz["dataAccessors"][v_metricAccessor].setMetric(v_metric)
                  }
                  if(tmp_group != ""){
                        v_group.name = tmp_group
                        v_group.sort = {
                            "name": "count",
                            "dir": "desc",
                        }
                        if(!$.isEmptyObject(v_metric)){
                            v_group.sort.name = v_metric.name
                            v_group.sort.metricFunc = v_metric.func
                        }
                       var accessor = window.viz["dataAccessors"][v_groupAccessor];
                       if(inList(list, v_chart)){ accessor.setGroup(v_group) }
                       else{ accessor.resetGroups([v_group]) }
                  }
                  $("#load-message").html("");
        }); //done function
    }); //then

    $("#metric").change(function() {
        var name = $( "#metric" ).val();
        var funct = $( "#func" ).val();
        var f = getObj(name, filters)
        if(f.type == "MONEY" || f.type == "NUMBER" || f.type == "INTEGER"){ //is a metric
            v_metric = { func: f.func.toLowerCase(), label: f.label, name: f.name, type: f.type }
            if(funct != ""){
                v_metric.func = funct;
            }
        }
        if(name == "count"){  //If the metric is count, the operator must be hidden
            $("#func").hide();
            $("#op-span").hide();
        }
        else{
            $("#func").show();
            $("#op-span").show();
        }
        console.group("Metric")
        console.log(name);
        console.log("accessor:", v_metricAccessor);
        console.log(v_metric);
        console.groupEnd()
        v_metric.name = name;
        var accessor = window.viz["dataAccessors"][v_metricAccessor];
        accessor.setMetric(v_metric)
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
            console.log("Accessor:", v_groupAccessor);
            console.log(group);
            console.groupEnd()
            var accessor = window.viz["dataAccessors"][v_groupAccessor];
            if(inList(list, v_chart)){
                accessor.setGroup(v_group)
            }
            else{
                accessor.resetGroups([v_group]);
            }
    });


    $("#func").change(function() {
            var funct = $("#func").val();
            list = ["KPI"]
            if(funct == ""){
                //If no operation, set the default operation of the metric
                var f = getObj(v_metric.name, filters)
                v_metric.func = f.func.toLowerCase()
                if(!inList(list, v_chart)){
                    v_group.sort.metricFunc = v_metric.func.toLowerCase()
                }
            }
            else{
                v_metric.func = funct;
                if(!inList(list, v_chart)){
                    v_group.sort.metricFunc = funct;
                }
            }
            console.group("Function")
            console.log(funct);
            console.log("met", v_metric);
            console.log("group", v_group);
            console.groupEnd()
            var mAccessor = window.viz["dataAccessors"][v_metricAccessor];
            var gAccessor = window.viz["dataAccessors"][v_groupAccessor];
            mAccessor.setMetric(v_metric)
            list = ["Donut","Packed","Scatter","Pie","Tree","Word"]
            if(inList(list, v_chart)){
                gAccessor.setGroup(v_group)
            }
            else{
                gAccessor.resetGroups([v_group]);
            }
    });
})

