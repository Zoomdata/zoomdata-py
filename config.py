chart = 'Bars'
source = 'Real Time Sales'
applicationConfig = { 'secure': True, 'host': 'pubsdk.zoomdata.com', 'port': 8443, 'path': '/zoomdata' }
queryConfig = { 'tz': 'UTC', 'filters': [] }
credentials = "56e966b8e4b03818a87e4547" #Real Time Sales
# credentials =  '572a14a5e4b0ad64f3a2d0ab' #Ticket Sales
# credentials =  '56ec8877e4b0c1680babc247' #Lending Club
paths = {
          'ZoomdataSDK':'https://pubsdk.zoomdata.com:8443/zoomdata/sdk/2.0/zoomdata-client.min',
          'jquery': 'https://ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min'
}
metric = { "func": "sum", "label": "Actual Sales", "name": "price", "type": "MONEY" }
groups = { "name": "usercity",
                   "limit": 40,
                   "sort": { "name":"price", "dir": "desc", "metricFunc":"sum" }}
# 
# 
"""
These values take care of the filters
  name: The drop down ids, the variables names for metric and groups, and the selectors in jquery to 
        get the values of the dropdowns
  attr: The name of the dataAccessor variable
  function: the name of the function used to modify the dataAccessor value
  params: the parameters of the function. So far they match the key 'name'
"""
dim, met  = 'group', 'metric'
metricParams = {'name': met, 
                'metricVar': met, 
                'groupVar': dim, 
                'attr':'Metric', 
                'function':'setMetric', 
                'params':met}

groupParams  = {'name': dim, 
                'metricVar': met, 
                'groupVar': dim, 
                'attr':'Multi Group By', 
                'function':'resetGroups', 
                'params':dim}

