class Template(object):

    def __init__(self):
        # RequireJS CDN
        self.requirejs = '<script src="https://cdnjs.cloudflare.com/ajax/libs/require.js/2.2.0/require.min.js"></script>'

        #Iframe where everything will be rendered
        self.iframe = """<iframe 
                            srcdoc='<div align="center">%s %s</div>' 
                            src='' 
                            width='%s' 
                            height='%s' 
                            sandbox='allow-scripts' 
                            frameborder='0'>
                        </iframe> """ 

        # Select and option string formatters
        self.selectFmt = '''<span>%s</span>
                            <select id="%s" style="margin-right:20px; margin-left:5px">%s<select>'''
        self.optionFmt = '<option value="%s">%s</option>'

        # Div where the chart is rendered (by echartjs)
        self.divChart = '<div id="%s" style="width:%spx; height:%spx; top:20%%"></div>'

        # Javascript tags to enclose all the js code
        self.scriptTags = '<script type="text/javascript">%s %s</script>' 

        # Container div for the filters (metric, dimension) drop-downs
        self.divFilters = '<div style="display:inline-block" align="center">%s</div>' 
        # The string keys for this templates are initially defined as metricParams/groupParams
        # in the file config.js, the can be modified later by the user changing the respective
        # ZD attrs
        # Drop-down for the dimension
        self.groupFilter= ''' $("#%(name)s").change(function() {
                                var name = $( "#%(name)s option:selected" )[0].value;
                                var f = getObj(name, filters)
                                var accessorAttr = groupAccessor
                                if(f.type == "ATTRIBUTE"){ //is a dimension
                                    %(groupVar)s.name = f.name
                                    %(groupVar)s.sort.name = %(metricVar)s.name
                                    %(groupVar)s.sort.metricFunc = %(metricVar)s.func
                                }
                                console.log("Group", name);
                                console.log("groupAccessor", groupAccessor);
                                %(name)s.name = $( "#%(name)s option:selected" )[0].value;
                                list = ["Donut","Packed","Scatter","Pie","Tree","Word"]
                                var accessor = window.viz["dataAccessors"][groupAccessor];
                                if(inList(list, chart)){
                                    accessor.setGroup(%(params)s)
                                }
                                else{
                                    accessor.resetGroups([%(params)s]);
                                }
                            });'''

        # Drop-down for the metric
        self.metricFilter= ''' $("#%(name)s").change(function() {
                                var name = $( "#%(name)s option:selected" )[0].value;
                                var f = getObj(name, filters)
                                if(f.type == "MONEY" || f.type == "NUMBER" || f.type == "INTEGER"){ //is a metric
                                    %(metricVar)s = { func: f.func.toLowerCase(), label: f.label, name: f.name, type: f.type }
                                    console.log("Metric object:", %(metricVar)s )
                                }
                                console.log("Metric:", name);
                                console.log("metricAccessor:", metricAccessor);
                                %(name)s.name = $( "#%(name)s option:selected" )[0].value;
                                var accessor = window.viz["dataAccessors"][metricAccessor];
                                accessor.setMetric(%(params)s)
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
                                    if (k.indexOf("etric") > -1) {
                                        metricAccessor = k;
                                    }
                                }
                           });
                          var metricSelect = $("#%(met)s");
                          var dimensionSelect = $("#%(dim)s");
                          gFlag = false;
                          mFlag = false;
                          $.each(window.viz.source.objectFields, function() {
                              console.log(this)
                              filters.push(this);
                              if(this.visible){
                                  if(this.type == "NUMBER" || this.type == "MONEY" || this.type == "INTEGER"){
                                       if(!mFlag){
                                            %(met)s = { func: this.func.toLowerCase(), 
                                                        label:this.label, 
                                                        name: this.name, 
                                                        type: this.type }
                                             mFlag = true; //Optimization purposes
                                       }
                                       metricSelect.append($("<option />").val(this.name).text(this.label));
                                  }
                                  else if(this.type == "ATTRIBUTE") { 
                                      %(dim)s.name = this.name
                                      %(dim)s.sort.name = %(met)s.name
                                      %(dim)s.sort.metricFunc = %(met)s.func
                                      dimensionSelect.append($("<option />").val(this.name).text(this.label)) 
                                  }
                              }
                          });
                        '''
