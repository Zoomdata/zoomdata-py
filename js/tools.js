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
