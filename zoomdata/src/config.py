# ===================================================================
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#  
#      http://www.apache.org/licenses/LICENSE-2.0
#  
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#  
# ===================================================================

#========== MAIN CONFIGURATION ======================
chart = 'Bars'
paths = {
          'ZoomdataSDK':'https://sdk.zoomdata.com:8443/zoomdata/sdk/2.0/zoomdata-client.min',
          'jquery': 'https://ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min'
}
config = {
        # Main App configurations
        'host': 'sdk.zoomdata.com', 
        'port': 8443,
        'path': '/zoomdata',
        'secure': True,
        "headers":{'Content-Type': 'application/vnd.zoomdata.v1+json', 'Authorization': False},
        # Mongo DB parameters
        'mongoServer': 'sdk.zoomdata.com', 
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

