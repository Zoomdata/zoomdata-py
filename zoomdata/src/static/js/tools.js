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
 */

function setPickers(htmlStr, pickersVal) {
    if (pickersVal.length != undefined) { //When is a multi-metric chart
        for (pos in pickersVal) {
            //Update the checkbox
            val = pickersVal[pos].name
            if (htmlStr.indexOf(val) > -1) {
                oldStr = "value= \"" + val + "\""
                newStr = oldStr + " checked=\"checked\""
                htmlStr = htmlStr.replace(oldStr, newStr)
                    //Update the function select
                frag = htmlStr.split(val)
                val = pickersVal[pos].func
                oldStr = "\"" + val + "\""
                newStr = oldStr + " selected=\"selected\""
                replace = frag[4].replace(oldStr, newStr)
                htmlStr = htmlStr.replace(frag[4], replace)
            }
        }
    }
    fuseField = pickersVal.hasOwnProperty("form") ? true:false
    for (key in pickersVal) {
        val = pickersVal[key]
        if(typeof(val) == "string"){
            val = val.replace("$","")
        }
        if(!fuseField || (fuseField && key !="name") ){
            if (htmlStr.indexOf(val) > -1) {
                if(key == "sort"){
                        oldStr = "\"" + val + "\""
                        var index = htmlStr.lastIndexOf(oldStr);
                        newStr = oldStr + " selected=\"selected\">"
                        sortDrop = htmlStr.substr(index);
                        sortDrop = sortDrop.replace(oldStr + ">", newStr)
                        htmlStr = htmlStr.substring(0, index) + sortDrop
                }else{
                        //Pickers
                        oldStr = "\"" + val + "\""
                        newStr = oldStr + " selected=\"selected\">"
                        htmlStr = htmlStr.replace(oldStr + ">", newStr)
                    }
            }
        }
    }
    return htmlStr
}


function loadDefinitionPickers(){
    //Loads and parse the default visualization values(dimensions and metrics) stored 
    //in the visualization definition
    pickerVals = {}
    groupBy = "Group By"
    dim = window.viz.dataAccessors.getDimensionAccessors()
    groupCounts = 1
    for (var i = 0; i < dim.length; i++) {
        for (acc in dim[i]){
            try{
                groups = dim[i][acc].getGroup()
            }
            catch(err){
                groups = dim[i][acc].getFields() //Maps
            }
            groups = (groups != null ) ? [groups]: dim[i][acc].getGroups()
            for (var g = 0; g < groups.length; g++) {
                accesor = acc
                if(acc == "Multi Group By"){
                    if(groups[g].type == "ATTRIBUTE"){
                        accesor = groupBy
                        //Heat Map & Floating Bubbles contain Group 1 and 2 instead of Group By
                        if(groupCounts > 1){
                          accesor = "Group "+groupCounts.toString()
                          if(pickerVals.hasOwnProperty(groupBy)){
                              pickerVals["Group 1"] = pickerVals[groupBy]
                              delete pickerVals[groupBy]
                          }
                        } 
                        groupCounts += 1
                    }
                    else{
                        accesor = "Trend Attribute"
                    }
                }
                field = groups[g].form == undefined ? groups[g].name: groups[g].form
                pickerVals[accesor] ={
                    name:  groups[g].name,
                    sort:  groups[g].sort.name,
                    label: groups[g].label,
                    dir:   groups[g].sort.dir,
                    limit: groups[g].limit,
                    type:  groups[g].type
                } 
                if(groups[g].sort.metricFunc) pickerVals[accesor].mfunc = groups[g].sort.metricFunc
                if(groups[g].func) pickerVals[accesor].func = groups[g].func
                if(groups[g].args) pickerVals[accesor].args = groups[g].args
                if(groups[g].form){
                    pickerVals[accesor].form = groups[g].form
                    pickerVals[accesor].forms = groups[g].forms
                }
            }
        }
    }

    //Load the metrics
    met = window.viz.dataAccessors.getMetricAccessors()
    for (var i = 0; i < met.length; i++) {
        for(acc in met[i]){
            m = met[i][acc].getMetric()
            m = (m != null ) ? m: met[i][acc].getMetrics()
            if(m.length == undefined ){ //Is only one metric
                pickerVals[acc] = {
                    name: m.name,
                    type: m.type,
                    func: m.func,
                    label: m.label
                } 
            }
            else{ //Multimetric charts
                pickerVals[acc] =[]
                for(k=0; k<m.length; k++){
                    pickerVals[acc].push({
                        met: m[k].name,
                        type: m[k].type,
                        func: m[k].func,
                        label: m[k].label
                    })
                }
            }
        }
    }
    return pickerVals
}


function checkValue(val){
    //Check if the fields specified by the user in graph() are correctly
    //Also support the field name or field label: qtysold / Quantity Sold 
    fieldNames = dimensionFields.fields.concat(metricFields.fields)
    fieldLabels = dimensionFields.labels.concat(metricFields.labels)
    if($.inArray(val, fieldNames) > -1) return val; 
    pos = $.inArray(val, fieldLabels)
    if(pos > -1) return fieldNames[pos];
    return "count"
}

function getValue(oldval, newval, accessor=false){
    if(newval){
        if(accessor){ 
            console.log(accessor);
            //In multigroup user pickers can be:
            //attr:"fieldname" or attr:["field1","field2"]
            if(typeof(newval) == "string"){
                if(accessor == "Group 1") return checkValue(newval);
                return oldval;
            }
            else{
                //Get what group is (1,2, etc...)
                pos = parseInt(accessor.split(" ")[1])
                console.log("pos", pos);
                if(newval.length >= pos) return checkValue(newval[pos - 1]);
                return oldval;
            }
        }
        return checkValue(newval);
    }
    return oldval
}


function loadUserPickers(){
    mgroupRegex = /Group [1-9]/g
    for (acc in v_pickersValues){
        if(acc == "Group By"){
            v_pickersValues[acc].name = getValue(v_pickersValues[acc].name, v_defPicker.field)
            if(v_defPicker.limit) v_pickersValues[acc].limit = v_defPicker.limit
            setDimension(acc)
        }
        else if(acc.match(mgroupRegex)){
            v_pickersValues[acc].name = getValue(v_pickersValues[acc].name , v_defPicker.field, acc)
            if(v_defPicker.limit) v_pickersValues[acc].limit = v_defPicker.limit
            setDimension(acc)
        }
        else if(acc == "Trend Attribute"){
            v_pickersValues[acc].name = getValue(v_pickersValues[acc].name, v_defPicker.trend)
            if(v_defPicker.time) v_pickersValues[acc].func = v_defPicker.time
            setDimension(acc)
        }
        else if(acc == "Metric"){
            v_pickersValues[acc].name= getValue(v_pickersValues[acc].name, v_defPicker.metric)
            if(v_defPicker.func) v_pickersValues[acc].func = v_defPicker.func
            setMetric(acc)
        }
        else if(acc == "Size"){
            v_pickersValues[acc].name = getValue(v_pickersValues[acc].name, v_defPicker.metric)
            if(v_defPicker.func) v_pickersValues[acc].func = v_defPicker.func
            setMetric(acc)
        }
        else if(acc == "Y Axis"){
            v_pickersValues[acc].name = getValue(v_pickersValues[acc].name, v_defPicker.y)
            if(v_defPicker.yop) v_pickersValues[acc].func = v_defPicker.yop
            setMetric(acc)
        }
        else if(acc == "X Axis"){
            v_pickersValues[acc].name = getValue(v_pickersValues[acc].name, v_defPicker.x)
            if(v_defPicker.xop) v_pickersValues[acc].func = v_defPicker.xop
            setMetric(acc)
        }
        else if(acc == "Y1 Axis"){
            v_pickersValues[acc].name = getValue(v_pickersValues[acc].name, v_defPicker.y1)
            if(v_defPicker.y1op) v_pickersValues[acc].func = v_defPicker.y1op
            setMetric(acc)
        }
        else if(acc == "Y2 Axis"){
            v_pickersValues[acc].name = getValue(v_pickersValues[acc].name, v_defPicker.y2)
            if(v_defPicker.y2op) v_pickersValues[acc].func = v_defPicker.y2op
            setMetric(acc)
        }
    }
}

function makeTable(rows, attrs){
    table =  "<table"
    tableEnd  =  "</table>"
    for (attr in attrs) {
      if(attrs[attr] === false) continue;
      table += " " + attr + "=\" " + attrs[attr] + "\"";

    }
    table += ">"
    rows.forEach(function(row){
        tr = "<tr>"
        row.forEach(function(val){
            tr += "<td>"+val+"</td>"
        })
        tr += "</tr>"
        table += tr
    })
    return table + tableEnd
}

function buildHTML(tag, html, attrs){
  var h = "<" + tag;
  for (attr in attrs) {
    if(attrs[attr] === false) continue;
    h += " " + attr + "= \"" + attrs[attr] + "\"";
  }
  return h += html ? ">" + html + "</" + tag + ">" : "/>";
}

function getDimensionGroup(accessor){
    val = v_pickersValues[accessor]
    if( val.type == "TIME" || val.type == "ATTRIBUTE" || 
      ( (val.type == "NUMBER" || val.type == "INTEGER" || val.type == "MONEY") && v_isHistogram ) ){
        group = {
            "name": val.name,
            "label": val.label,
            "sort": {
                "name": val.sort,
                "dir": val.dir,
                "metricFunc": val.mfunc
            },
            "limit": val.limit,
            "type": val.type
        }
        if (val.type == "TIME") {
            group.func = val.func; //The granularity
            group.sort.name = group.name; //The same time field
            delete group.sort.metricFunc; //No operation
        }
        if (group.sort.name == "count" || group.sort.name == group.name) {
            delete group.sort.metricFunc;
        }
        if (v_isHistogram) {
            group.func = val.func
            group.args = val.args
        }
        if(val.form){
            group.form = val.form
            group.forms = val.forms
        }
        return group
    }
    return false
}


function setDimension(accessorName){
    multiGroup = "Multi Group By";
    if(window.viz.dataAccessors.hasOwnProperty(multiGroup)){
        accessor = window.viz.dataAccessors[multiGroup];
        groups = [];
        for(acc in v_pickersValues){
            g = getDimensionGroup(acc)
            if(g) groups.push(getDimensionGroup(acc));
        }
        console.info(multiGroup, groups);
        accessor.resetGroups(groups);
    }
    else{
        accessor = window.viz.dataAccessors[accessorName];
        group = getDimensionGroup(accessorName);
        console.info(accessorName, group);
        accessor.resetGroup(group);
     }
}

function getMetricGroup(accessor){
    val = v_pickersValues[accessor]
    if(val.length == undefined){
        if(val.type == "NUMBER" || val.type == "INTEGER" || val.type == "MONEY"){
            metric = { 
                      "name": val.name, 
                      "func": val.func, 
                      "label": val.label, 
                    }
            if(val.met == "count"){
                metric.func = ""
            } 
            return metric 
        }
    }
    else{
        metrics = []
        for(pos in val) {
            metrics.push({ 
                      "name": val[pos].name, 
                      "func": val[pos].func, 
                      "label": val[pos].label, 
                })
        }
        return metrics
    }
    return false
}

function setMetric(accessorName) {
    metric = getMetricGroup(accessorName)
    accessor = window.viz.dataAccessors[accessorName];
    console.log(accessorName, metric)
    try{
        accessor.setMetric(metric)
    }
    catch(err){
        //This hack is mostly to fix the Line Trend: Multiple Metric bug
        accessor.isColor = false; 
        accessor.resetMetrics(metric)
    }
}

function getFusionLabel(field){
    //Returns the fusion field label: ie Event:ID or Event:Name
    label = _(fusionFields).filter(f => f.fields.indexOf(field) > -1).map(f => f.label).value()[0]
    obj = _(fusionFields).filter({"label":label}).value()[0]
    return label +":"+obj.labels[obj.fields.indexOf(field)]
}

