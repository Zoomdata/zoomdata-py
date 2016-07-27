function getKeys(obj) {
    var keys = [], name;
    for (name in obj) {
        if (obj.hasOwnProperty(name)) {
            keys.push(name);
        }
    }
    return keys;
}

function setPickers(htmlStr, pickersVal){
    for(key in pickersVal){
        val = pickersVal[key]
        if(htmlStr.indexOf(val) > -1){
            //Pickers
            oldStr = "\""+val+"\""
            newStr = oldStr + " selected=\"selected\""
            //Inputs: HOW TO???
            htmlStr = htmlStr.replace(oldStr, newStr)
        }
    }
   return htmlStr     
}


function loadDefinitionPickers(){
        pickerVals = {}
        dim = window.viz.dataAccessors.getDimensionAccessors()
        groupCounts = 1
        for (var i = 0; i < dim.length; i++) {
            for (acc in dim[i]){
                groups = dim[i][acc].getGroup()
                groups = (groups != null ) ? [groups]: dim[i][acc].getGroups()
                for (var g = 0; g < groups.length; g++) {
                    accesor = acc
                    if(acc == "Multi Group By"){
                        if(groups[g].type == "ATTRIBUTE"){
                            accesor = "Group By"
                            //Heat Map contain Group 1 and 2 instead of Group By
                            if(groupCounts > 1){
                              accesor = "Group "+groupCounts.toString()
                              if(pickerVals.hasOwnProperty("Group By")){
                                  pickerVals["Group 1"] = pickerVals["Group By"]
                                  delete pickerVals["Group By"]
                              }
                            } 
                            groupCounts += 1
                        }
                        else{
                            accesor = "Trend Attribute"
                        }
                    }
                    pickerVals[accesor] ={
                        field: groups[g].name,
                        sort:  groups[g].sort.name,
                        time:  groups[g].func,
                        mfunc: groups[g].sort.metricFunc,
                        dir:   groups[g].sort.dir,
                        limit: groups[g].limit,
                        type: groups[g].type
                    } 
                }
            }
        }

    met = window.viz.dataAccessors.getMetricAccessors()
    for (var i = 0; i < met.length; i++) {
        for(acc in met[i]){
            m = met[i][acc].getMetric()
            m = (m != null ) ? [m]: met[i][acc].getMetrics()
            for(k=0; k<m.length; k++){
                pickerVals[acc] = {
                    met: m[k].name,
                    func: m[k].func
                } 
            }
        }
    }
    return pickerVals
}

function getValue(oldval, newval){
    if(newval){
        if($.inArray(newval, fieldNames) > -1) return newval;
        pos = $.inArray(newval, fieldLabels)
        if(pos > -1) return fieldNames[pos];
    }
    return oldval
}


function loadUserPickers(){
    for (acc in v_pickersValues){
        if(acc == "Group By"){
            v_pickersValues[acc].field = getValue(v_pickersValues[acc].field, v_defPicker.field)
            if(v_defPicker.limit) v_pickersValues[acc].limit = v_defPicker.limit
            setDimension(acc)
        }
        else if(acc == "Trend Attribute"){
            v_pickersValues[acc].field = getValue(v_pickersValues[acc].field, v_defPicker.trend)
            if(v_defPicker.time) v_pickersValues[acc].time = v_defPicker.time
            setDimension(acc)
        }
        else if(acc == "Metric"){
            v_pickersValues[acc].met = getValue(v_pickersValues[acc].met, v_defPicker.metric)
            if(v_defPicker.func) v_pickersValues[acc].func = v_defPicker.func
            setMetric(acc)
        }
        else if(acc == "Size"){
            v_pickersValues[acc].met = getValue(v_pickersValues[acc].met, v_defPicker.metric)
            if(v_defPicker.func) v_pickersValues[acc].func = v_defPicker.func
            setMetric(acc)
        }
        else if(acc == "Y1 Axis"){
            v_pickersValues[acc].met = getValue(v_pickersValues[acc].met, v_defPicker.y1)
            if(v_defPicker.y1op) v_pickersValues[acc].func = v_defPicker.y1op
            setMetric(acc)
        }
        else if(acc == "Y2 Axis"){
            v_pickersValues[acc].met = getValue(v_pickersValues[acc].met, v_defPicker.y2)
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
            tr += "<td style=\"text-align:right\">"+val+"</td>"
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


function getDimensionGroups(){
    groups = []
    for(acc in v_pickersValues){
        group = v_pickersValues[acc]
        if (group.type == "ATTRIBUTE" || group.type == "TIME"){
            g = { "name": group.field, 
                  "sort":{"name":group.sort, "dir":group.dir}, 
                  "limit":group.limit, 
                  "type": group.type
                }
            if(group.type == "TIME"){ g.func = group.time}
            groups.push(g)
        }
    }
    return groups
}

function setDimension(accessorName){
    val = v_pickersValues[accessorName]
    if($.inArray("Multi Group By", accesorsKeys) > -1){
        accessorName = "Multi Group By"    
    }
    accessor = window.viz["dataAccessors"][accessorName];
    group = {   "name": val.field, 
                "sort":{
                        "name": val.sort, 
                        "dir": val.dir }, 
                "limit": val.limit, 
                "type": val.type}
    if(val.type == "TIME") group.func = val.time
    try{
        accessor.resetGroup(group)
    }
    catch(err){
        accessor.resetGroups(getDimensionGroups());
    }
}

function setMetric(accessorName){
    val = v_pickersValues[accessorName]
    metric = {"name": val.met, "func": val.func}
    accessor = window.viz["dataAccessors"][accessorName];
    console.log(metric)
    accessor.setMetric(metric)
}
