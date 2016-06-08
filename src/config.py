#========== MAIN CONFIGURATION ======================
chart = 'Bars'
paths = {
          'ZoomdataSDK':'https://pubsdk.zoomdata.com:8443/zoomdata/sdk/2.0/zoomdata-client.min',
          'jquery': 'https://ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min'
}
config = {
        # Main App configurations
        'host': 'pubsdk.zoomdata.com', 
        'port': 8443,
        'path': '/zoomdata',
        'secure': True,
        "headers":{'Content-Type': 'application/vnd.zoomdata.v1+json', 'Authorization': False},
        # Mongo DB parameters
        'mongoServer': 'pubsdk.zoomdata.com', 
        'mongoPort': 27017,
        'mongoSchema': 'zoom',
        "accountID": '56e9669ae4b03818a87e452c'
    }

# ============ VISUALIZATION =============================
queryConfig = { 'tz': 'UTC', 'filters': [] }
metric = { "func": "sum", "label": "Actual Sales", "name": "price", "type": "MONEY" }
groups = { "name": "usercity",
                   "limit": 40,
                   "sort": { "name":"price", "dir": "desc", "metricFunc":"sum" }}
"""
These values take care of the filters
  name: The drop down ids, the variables names for metric and groups, and the selectors in jquery to 
        get the values of the dropdowns
  params: the parameters of the function. So far they match the key 'name'
  NOTE: This configurations are not available for the user
"""
dim, met  = 'group', 'metric'
metricParams = {'name': met, 'metricVar': met, 'groupVar': dim, 'params':met}
groupParams  = {'name': dim, 'metricVar': met, 'groupVar': dim, 'params':dim}

# ============== SOURCE =================================================
connReq = { 
        'mongo': {  "name": "",
                    "connectorName": "mongo",
                    "connectorParameters": {
                            "username": "",
                            "password": "",
                            "host": "localhost",
                            "port": "27017",
                            "db": "zoom"
                        },
                    "created": { "by": { "username": "admin" }}
                }, #end mongo connector
        'spark': {}
    }

sourceReq = {
    "cacheable": True,
    "created": { "by": { "username": "admin" }},
    "description": "Created by Jupyter Notebook session",
    "name": "",
    "sourceParameters": { "collection": "" },
    "sparked": False
}

