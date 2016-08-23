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

//Dimension Handler
$("body").on("click", "button.btn-dimension", function () {
    var btn = $(this)
    var btnAccessor = btn.attr("data-name")
    var limitInput = buildHTML("input","",{ id:"limit", 
                                            value: v_pickersValues[btnAccessor].limit, 
                                            class:"value-input"})
    //Place in the sort by select, the selected dimension
    dim = v_pickersValues[btnAccessor].name
    label = dimensionFields.labels[dimensionFields.fields.indexOf(dim)]
    var type = dimensionFields.types[dimensionFields.fields.indexOf(dim)]
    //If no attr label found (due to this.false) then is a fusion source
    if(label == undefined){
        label = v_pickersValues[btnAccessor].label
    } 
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
            var label = this.$b.find("#dimension option:selected").text()
            //Save the values
            type = dimensionFields.types[dimensionFields.fields.indexOf(field)]
            v_pickersValues[btnAccessor] = {
                name: field,
                func: time,
                sort: sortby,
                mfunc: metFunc,
                dir: dir,
                limit: parseInt(limit),
                type: type
            }
            //Check if is a fusion attribute the value is not in the fields names (this.visible == false)
            if(dimensionFields.fields.indexOf(field) == -1)
            {
               //Search the fuse attr (Label:Form)
               args = label.split(":")
               grp = _(window.viz.source.fusedAttributes).filter({"label":args[0]}).value()[0]
               //Fill the picker value
               v_pickersValues[btnAccessor].form = field
               v_pickersValues[btnAccessor].name = grp.name
               v_pickersValues[btnAccessor].forms = grp.forms
               v_pickersValues[btnAccessor].label = args[0]
            }
            //If selected sortby is the attribute name, func must be null
            if(metricFields.fields.indexOf(sortby) == -1){
                v_pickersValues[btnAccessor].mfunc = undefined
            }
            //Set the dimension
            setDimension(btnAccessor)
            //Update the button text with the selected dimension
            fieldLabel = btnAccessor + ": <b>"+label+"</b>"
            if(type == "TIME") { 
                fieldLabel += "<b> ("+time+")</b>"
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
    if(v_pickersValues[btnAccessor].name == "count"){
        find = "id= \"func\""
        rep = find + " disabled"
        newFuncSelect = funcSelect.replace(find, rep)
    }
    table = [["Metric",metricSelect],["Operator", newFuncSelect ]]
    //var content = multiMetric
    var content = makeTable(table,{class: "pickers"})
    content = setPickers(content ,v_pickersValues[btnAccessor])
    $.confirm({
        title: btnAccessor,
        theme: "black",
        confirmButtonClass: "btn-success",
        confirmButton: "Apply",
        content: content,
        confirm: function () {
            var met = this.$b.find("#metric").val()
            var func = this.$b.find("#func").val()
            var label = this.$b.find("#metric option:selected").text()
            func = (met == "count") ? "" : func
            //Save the values
            type = metricFields.types[metricFields.fields.indexOf(met)]
            v_pickersValues[btnAccessor] = {
                name: met,
                func: func,
                type: type
            }
            //Set the metric
            setMetric(btnAccessor)
            //Update the button text with the selected metric
            metLabel = btnAccessor+": <b>"+label+"</b>"
            if(func != ""){
                metLabel += "<b> ("+func+")</b>" 
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
            var label = this.$b.find("#metric option:selected").text()
            var args = this.$b.find("#args").val()
            type = metricFields.types[metricFields.fields.indexOf(field)]
            //Save the values
                v_pickersValues[btnAccessor] = {
                    field: field,
                    sort: field,
                    func: histgrm,
                    mfunc: undefined,
                    label: label,
                    args: parseInt(args),
                    dir: "desc",
                    limit: 10000,
                    type: type
                }

            //Set the metric
            setDimension(btnAccessor)
            //Update the button text with the selected metric
            label = "Histogram: <b>"+label+"</b>"
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
                type = metricFields.types[metricFields.fields.indexOf(v)]
                v_pickersValues[btnAccessor].push({
                    name: v,
                    label: this.$b.find("label[for=\""+v+"\"]").text(),
                    func: this.$b.find("select#"+v).val(),
                    type: type
                })
            }
            console.log(v_pickersValues)
            //Set the metric
            setMetric(btnAccessor)
            //Update the button text with amount of selected metrics
            metLabel = btnAccessor+": <b> ("+values.length.toString()+" selected)</b>"
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
    text = $("select#dimension option:selected").text()
    value = $( "select#dimension option:selected" ).val()
    //Validate multimetric fields    
    if(text.indexOf(":") > -1){ 
        text = text.split(":")[0] 
        value = _(fusionFields).filter({"label":text}).value()[0].name
    }
   $("select#metric").append($("<option>", { value:value, text: text }));
   if($("select#dimension option:selected").text() != $( "select#metric option:selected" ).text()){
      $("select#func").prop("disabled", false);
   }
})

$("body").on("change", "select#metric", function() {
    text = $("select#dimension option:selected").text()
    if(text.indexOf(":") > -1){ 
        text = text.split(":")[0] 
    }
    if (text == $("select#metric option:selected").text()) {
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
