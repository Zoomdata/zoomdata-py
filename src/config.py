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
    }

# ============ VISUALIZATION =============================
queryConfig = { 'tz': 'UTC', 'filters': [] }
metric = { "func": "sum", "label": "Actual Sales", "name": "price", "type": "MONEY" }
groups = { "name": "usercity",
                   "limit": 40,
                   "sort": { "name":"price", "dir": "desc", "metricFunc":"sum" }}

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

