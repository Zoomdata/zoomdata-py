class Template(object):

    def __init__(self):
        # RequireJS CDN
        self.requirejs = '<script src="https://cdnjs.cloudflare.com/ajax/libs/require.js/2.2.0/require.min.js"></script>'
        self.jqueryjs = '<script src="https://ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js"></script>'
        self.zdclientjs= '<script src="https://pubsdk.zoomdata.com:8443/zoomdata/sdk/2.0/zoomdata-client.js"></script>'

        #Iframe where everything will be rendered
        self.iframe = """
                        <script type="text/javascript">var kernel = IPython.notebook.kernel</script>
                        <iframe 
                            srcdoc='<div align="center">%s %s</div>' 
                            src='' 
                            width='%s' 
                            height='%s' 
                            frameborder='0'>
                        </iframe> """ 

        self.loadmsg = '<p id="load-message" style="margin-top:10px" align="center">Loading visualization...</p>'

        # Javascript tags to enclose all the js code
        self.scriptTags = '<script type="text/javascript">%s %s</script>' 

        # Select and option string formatters
        self.selectFmt = '''<span id="%s">%s</span>
                            <select id="%s" style="margin-right:20px; margin-left:5px">%s<select>'''
        self.optionFmt = '<option value="%s">%s</option>'

        # Div where the chart is rendered (by echartjs)
        self.divChart = '<div id="%s" style="width:%spx; height:%spx; top:20%%"></div>'

        # Container div for the filters (metric, dimension) drop-downs
        self.divFilters = '<div style="display:inline-block" align="center">%s</div>' 
        # The string keys for this templates are initially defined as metricParams/groupParams
        # in the file config.js, the can be modified later by the user changing the respective
        # ZD attrs
        # Drop-down for the dimension
        self.groupPicker = ''' $("#group").change(function() {
                                var name = $( "#group option:selected" )[0].value;
                                var funct = $( "#func option:selected" )[0].value;
                                var f = getObj(name, filters)
                                var accessorAttr = groupAccessor
                                if(f.type == "ATTRIBUTE"){ //is a dimension
                                    group.name = f.name
                                    if(metric.name != "count"){
                                        group.sort.name = metric.name
                                        group.sort.metricFunc = metric.func
                                        if(funct != ""){
                                            group.sort.metricFunc = funct 
                                        }
                                    }
                                    else{
                                        group.sort = {"name":"count","dir":"desc"}
                                    }
                                }
                                console.group("Group By")
                                console.log(name);
                                console.log("Accessor:", groupAccessor);
                                console.log(group);
                                console.groupEnd()
                                group.name = $( "#group option:selected" )[0].value;
                                list = ["Donut","Packed","Scatter","Pie","Tree","Word"]
                                var accessor = window.viz["dataAccessors"][groupAccessor];
                                if(inList(list, chart)){
                                    accessor.setGroup(group)
                                }
                                else{
                                    accessor.resetGroups([group]);
                                }
                            });'''

        # Drop-down for the metric
        # THe id of the html select is passed dinamically because there may be 2 metrics at the same
        # time for specific chart types
        self.metricPicker = ''' $("#%(metID)s").change(function() {
                                var picker = $("#%(metID)s").attr("id") //Need to know what metric is changed 1 or 2
                                var acc = metricAccessor;
                                if(picker.indexOf("2") > -1){
                                   acc = "Y2 Axis" //TODO: This must be setted dinamically
                                }
                                var name = $( "#%(metID)s" ).val();
                                var funct = $( "#func" ).val();
                                var f = getObj(name, filters)
                                if(f.type == "MONEY" || f.type == "NUMBER" || f.type == "INTEGER"){ //is a metric
                                    metric = { func: f.func.toLowerCase(), label: f.label, name: f.name, type: f.type }
                                    if(funct != ""){
                                        metric.func = funct;
                                    }
                                    variables[acc] = metric.name;
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
                                console.log("accessor:", acc);
                                console.log(metric);
                                console.groupEnd()
                                metric.name = name;
                                var accessor = window.viz["dataAccessors"][acc];
                                accessor.setMetric(metric)
                            });'''

        self.funcPicker = ''' $("#func").change(function() {
                                var funct = $( "#func option:selected" )[0].value;
                                if(funct == ""){
                                    //If no operation, set the default operation of the metric
                                    var f = getObj(metric.name, filters)
                                    metric.func = f.func.toLowerCase()
                                    group.sort.metricFunc = metric.func.toLowerCase()
                                }
                                else{
                                    metric.func = funct;
                                    group.sort.metricFunc = funct;
                                }
                                console.group("Function")
                                console.log(funct);
                                console.log("met", metric);
                                console.log("group", group);
                                console.groupEnd()
                                var mAccessor = window.viz["dataAccessors"][metricAccessor];
                                var gAccessor = window.viz["dataAccessors"][groupAccessor];
                                mAccessor.setMetric(metric)
                                list = ["Donut","Packed","Scatter","Pie","Tree","Word"]
                                if(inList(list, chart)){
                                    gAccessor.setGroup(group)
                                }
                                else{
                                    gAccessor.resetGroups([group]);
                                }
                            });'''

        # The body of .done callback. Used in the ZD __wrapper method. This function gets the result
        # from the ZD pubsdk, and fills the filters drop-downs using jquery, the only two variables needed
        # must match with the id of the html filters drop-downs
        self.doneBody=''' window.viz = result;
                          console.log("Thread:", window.viz);
                          var accesorsKeys = getKeys(window.viz.dataAccessors);
                          console.log("Accesors keys", accesorsKeys);
                          var metricFlag = false;
                          accesorsKeys.forEach(function(k) {
                                if (k.indexOf("roup") > -1) {
                                    groupAccessor = k;
                                } else { //Metric, Size and Colors are metrics
                                    if (!metricFlag) { 
                                        metricAccessor = k;
                                        metricFlag = true;
                                    }
                                    //When metricFlag is true, it means that a metric is setted as accessor
                                    if (k.indexOf("etric") > -1) {
                                        metricAccessor = k;
                                    }
                                }
                           });
                          var metricSelect1 = $("#metric1");
                          var metricSelect2 = $("#metric2");
                          var dimensionSelect = $("#group");
                          gFlag = false;
                          mFlag = false;
                          $.each(window.viz.source.objectFields, function() {
                              filters.push(this);
                              if(this.visible){
                                  if(this.type == "NUMBER" || this.type == "MONEY" || this.type == "INTEGER"){
                                       if(!mFlag){
                                            metric = { func: this.func.toLowerCase(), 
                                                        label:this.label, 
                                                        name: this.name, 
                                                        type: this.type }
                                             mFlag = true; //Optimization purposes
                                       }
                                       metricSelect1.append($("<option />").val(this.name).text(this.label));
                                       metricSelect2.append($("<option />").val(this.name).text(this.label));
                                  }
                                  else if(this.type == "ATTRIBUTE") { 
                                      group.name = this.name
                                      group.sort.name = metric.name
                                      group.sort.metricFunc = metric.func
                                      dimensionSelect.append($("<option />").val(this.name).text(this.label)) 
                                  }
                              }
                          });
                          $("#load-message").html("");
                        '''
