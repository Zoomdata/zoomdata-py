function getKeys(obj) {
    var keys = [], name;
    for (name in obj) {
        if (obj.hasOwnProperty(name)) {
            keys.push(name);
        }
    }
    return keys;
}

function getObj(name, filters){
    var obj = {}
    $.each(filters, function(){
        if(this.name == name){
            obj = this
        }
    })
    return obj
}

function inList(list, string){
    found = false;
    list.forEach(function(k){
        if(string.indexOf(k) > -1 || k.indexOf(string) > -1){
            found = true;
        }
    })
    return found
}

function getData(){
    rawData = window.viz.thread.getData()
    if(rawData.length == 0){
        console.log("Waiting for data")
        setTimeout(getData,50)
    }
    else{
        pyvar = {"data":false, "columns":[]}
        acc = window.viz.dataAccessors.getDimensionAccessors()
        for(var i=0;i < acc.length;i++){
            if(acc[i].hasOwnProperty("Multi Group By")){
                groups = acc[i]["Multi Group By"].getGroups()
                for(var g=0; g < groups.length; g++){
                    pyvar.columns.push(groups[g].name)
                }
            }
            else if(acc[i].hasOwnProperty("Group By")){
                group = acc[i]["Group By"].getGroup()
                pyvar.columns.push(group.name)    
            }
        }
        pyvar.data = rawData
        console.log(pyvar)
        pyvar = JSON.stringify(pyvar)
        pyvar = pyvar.replace("null","\"Null\"")
        pyvar = pyvar.replace("false","False")
        pyvar = pyvar.replace("true","True")
        parent.kernel.execute("ZD._rawVisualData = "+ pyvar)
    }
}
