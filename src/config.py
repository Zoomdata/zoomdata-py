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

charTypes = {
    "bars": "Bars",
    "bars-histo": "Bars: Histogram",
    "bars-multi": "Bars: Multiple Metrics",
    "boxplot": "Box Plot",
    "donut": "Donut",
    "fingerpaint": "Fingerpaint",
    "floating-bubbles": "Floating Bubbles",
    "heat-map": "Heat Map",
    "kpi": "KPI",
    "line-bars-trend": "Line & Bars Trend",
    "line-trend-attr": "Line Trend: Attribute Values",
    "line-trend-multi": "Line Trend: Multiple Metrics",
    "map-markers": "Map: Markers",
    "map-us": "Map: US Regions",
    "map-world": "Map: World Countries",
    "packed-bubbles": "Packed Bubbles",
    "pie": "Pie",
    "scatter-plot": "Scatter Plot",
    "table": "Table",
    "tree-map": "Tree Map",
    "word-cloud": "Word Cloud",
}

