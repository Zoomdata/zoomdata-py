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
                accessor = acc
                if(acc == "Multi Group By"){
                    if(groups[g].type == "ATTRIBUTE"){
                        accessor = groupBy
                        //Heat Map & Floating Bubbles contain Group 1 and 2 instead of Group By
                        if(groupCounts > 1){
                          accessor = "Group "+groupCounts.toString()
                          if(pickerVals.hasOwnProperty(groupBy)){
                              pickerVals["Group 1"] = pickerVals[groupBy]
                              delete pickerVals[groupBy]
                          }
                        } 
                        groupCounts += 1
                    }
                    else{
                        accessor = "Trend Attribute"
                    }
                }
                field = groups[g].form == undefined ? groups[g].name: groups[g].form
                pickerVals[accessor] = toPickerFormat(groups[g])
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
                pickerVals[acc] = toPickerFormat(m)
            }
            else{ //Multimetric charts
                pickerVals[acc] =[]
                for(k=0; k<m.length; k++){
                    pickerVals[acc].push(toPickerFormat(m[k]))
                }
            }
        }
    }
    return pickerVals
}

function toPickerFormat(field){
    picker = {}
    if(field.type == "ATTRIBUTE" || field.type == "TIME" ){
                picker = {
                    name:  field.name,
                    sort:  field.sort.name,
                    label: field.label,
                    dir:   field.sort.dir.toLowerCase(),
                    limit: field.limit,
                    type:  field.type
                } 
                if(field.sort.func) picker.mfunc = field.sort.func.toLowerCase()
                if(field.func) picker.func = field.func
                if(field.args) picker.args = field.args
                if(field.form){
                    picker.form = field.form
                    picker.forms = field.forms
                }
    }
    else{ //Metrics
        picker = {
            name:  field.name,
            type: field.type,
            func: field.func,
            label:field.label
        } 
        if(field.func) picker.func = field.func.toLowerCase()
    }
    return picker
}


function getValue(oldval, newval, accessor=false){
    if(newval){
        if(accessor){ //Is multi-group
            console.log(accessor);
            if(newval.length == 1){ 
                if(accessor == "Group 1") {
                    return toPickerFormat(newval)
                }
                return oldval;
            }
            else{
                //Get which group is (1,2, etc...)
                pos = parseInt(accessor.split(" ")[1])
                console.log("pos", pos);
                if(newval.length >= pos) {
                    return toPickerFormat(newval[pos - 1])
                }
                return oldval;
            }
        }
        return toPickerFormat(newval)
    }
    return oldval
}


function loadUserPickers(){
    mgroupRegex = /Group [1-9]/g
    for (acc in v_pickersValues){
        if(acc == "Group By"){
            if(v_defPicker.field){
                v_pickersValues[acc] = toPickerFormat(v_defPicker.field[0])
                setDimension(acc)
            }
        }
        else if(acc.match(mgroupRegex)){
            if(v_defPicker.field){
                v_pickersValues[acc] = getValue(v_pickersValues[acc] , v_defPicker.field, acc)
                setDimension(acc)
        }}
        else if(acc == "Trend Attribute"){
            if(v_defPicker.trend){
                v_pickersValues[acc] = toPickerFormat(v_defPicker.trend[0])
                setDimension(acc)
        }}
        else if(acc == "Metric" || acc == "Size" || acc == "Color Metric"){
            if(v_defPicker.metric){
                v_pickersValues[acc] = toPickerFormat(v_defPicker.metric[0])
                setMetric(acc)
        }}
        else if(acc == "Y Axis"){
            if(v_defPicker.y){
                v_pickersValues[acc] = toPickerFormat(v_defPicker.y[0])
                setMetric(acc)
        }}
        else if(acc == "X Axis"){
            if(v_defPicker.x){
                v_pickersValues[acc] = toPickerFormat(v_defPicker.x[0])
                setMetric(acc)
        }}
        else if(acc == "Y1 Axis"){
            if(v_defPicker.y1){
                v_pickersValues[acc] = toPickerFormat(v_defPicker.y1[0])
                setMetric(acc)
        }}
        else if(acc == "Y2 Axis"){
            if(v_defPicker.y2){
                v_pickersValues[acc]= gtoPickerFormat(v_defPicker.y2[0])
                setMetric(acc)
        }}
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
    if (val.name == "count")  return {"name":val.name, "label":volumeLabel}
    if (val.length == undefined) {
        if (val.type == "NUMBER" || val.type == "INTEGER" || val.type == "MONEY") {
            return { "name": val.name, "func": val.func, "label": val.label }
        }
    } else {
        metrics = []
        for (pos in val) {
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

