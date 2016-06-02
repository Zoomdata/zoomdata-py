chart = 'Bars'
source = 'Real Time Sales'
applicationConfig = { 'secure': True, 'host': 'pubsdk.zoomdata.com', 'port': 8443, 'path': '/zoomdata' }
queryConfig = { 'tz': 'UTC', 'filters': [] }
credentials = { 'key': "56e966b8e4b03818a87e4547" };
paths = {
          'ZoomdataSDK':'https://pubsdk.zoomdata.com:8443/zoomdata/sdk/2.0/zoomdata-client.min',
          'jquery': 'https://ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min'
}
metric = { "func": "sum", "label": "Actual Sales", "name": "price", "type": "MONEY" }
groups = { "name": "usercity",
                   "limit": 20,
                   "sort": { "name":"price", "dir": "desc", "metricFunc":"sum" }}
#This values must match the specified on the Thread object wich, depending on the chart type
metricParams = {'attr':'Metric', 'function':'setMetric', 'params':'metric'}
groupParams  = {'attr':'Multi Group By','function':'setGroup', 'params':'0, dimension'}
