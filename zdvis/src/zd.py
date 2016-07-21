#/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import json
import base64
import pickle
import pandas as pd
from time import sleep
from .rest import RestCalls
from .visdefinition import VisDefinition
from .visrender import VisRender
from .config import *
from .jsbuilder import JSBuilder
from .templates import Template
from IPython.display import display, HTML

rest = RestCalls()
vd = VisDefinition()
js = JSBuilder()
t = Template()
deps = ['ZoomdataSDK','jquery']

def data(resp):
    return resp.data.decode('ascii')

class ZDVisualization(object):

    """ ZDVisualization puts together all the javascript pieces
    needed to create a connection with the ZD SDK and fecth 
    the requested data. It finally renders the html and js into
    the notebook output dom through the HTML object """

    def __init__(self):
        """ To ensure maximum flexibility for the visualization configuration
        here must be setted all values that may change """

        #Main configurations
        self._conf = config
        protocol = 'https' if config['secure'] else 'http'
        self._serverURL = '%s://%s:%s%s' % (protocol, config['host'], config['port'], config['path'])
        self._source_credentials = {}
        self._sources_json_file = '/tmp/sources.json'

        if os.path.exists(self._sources_json_file):
            with open(self._sources_json_file,'r') as sc:
                self._source_credentials = json.load(sc)
        else: #Create it and leave it there
            with open(self._sources_json_file, 'w') as sc:
                json.dump(self._source_credentials, sc)
            #Change the mode so anyone can use read/write it
            os.chmod(self._sources_json_file,0o666)

        # User authentication
        self._user = ''
        self._account = ''
        self._token = ''

        # Dataframe fetching attrs
        self._dframe= ''
        self._logcount = 0
        # Visualization attrs
        self._source = ''
        self._chart = chart
        self._width = 800
        self._height = 400
        self._renderCount = 0 #To render a different chart each time
        self._paths = paths
        self._query = queryConfig
        self._credentials = ''  # This is the key to get the source key to get the visualization
        self._source_id = '' # This is the source id to get the source definition
        self._source_charts = [] # Active visualizations for the current source
        self._allowed_visuals = [] # All the visualizations names allowed by zoomdata
        self._variables = {}
        self._filters = {} # Filters defined by the user to narrow visualization results
        self._pickers = {} # Default pickers values for the visualization
        #Attrs for new source/collection creation
        self._connReq = connReq
        self._sourceReq = sourceReq

    def auth(self, server, user, password):
        cred = user+':'+password
        key = base64.b64encode(cred.encode('ascii'))
        key = 'Basic ' + key.decode('ascii')
        self._connReq['mongo']['created']['by']['username'] = user
        self._sourceReq['created']['by']['username'] = user
        self._conf['headers']['Authorization'] = key
        # Get the account
        if server:
            server.rstrip('/')
            self._serverURL = server
        self._account = rest.getUserAccount(self._serverURL, self._conf['headers'], user)
        self._user = user

    def __updateSourceFile(self):
        with open(self._sources_json_file, 'w') as sc:
            json.dump(self._source_credentials, sc)


    def _oauth(self, user):
        # Ideally this should go within data_handler
        self._user = user
        datafile = open('/var/userdata.pkl', 'rb')
        data = pickle.load(datafile)
        userdata = data.get(user, False)
        datafile.close()
        if userdata:
            self._account = userdata['accountId']
            self._token = userdata['token']
            key = "Bearer {}".format(userdata['token'])
            self._connReq['mongo']['created']['by']['username'] = user
            self._sourceReq['created']['by']['username'] = user
            self._conf['headers']['Authorization'] = key

    def register(self, sourceName, dataframe): 
        """Creates a new Zoomdata source using the specified parameters:
                Parameters:
                    sourceName: The name given for the new source
                    dataframe: Contains the data used to populate the source, commonly a pandas dataframe is used
        """
        if(self._conf['headers']['Authorization']):
            urlParams = { 'separator':',',
                          'contentType':'text/csv',
                          'includesHeader':'true',
                          'includesNewFields':'true' }
            #Convert dataframe from whatever it is to csv
            print('Parsing data...')
            try:
                df = dataframe.to_csv()
            except:
                print('Invalid dataframe')

            resp = rest.createSourceFromData(self._serverURL, self._conf['headers'], \
                                            self._account, sourceName, df, urlParams)
            if resp:
                # Avoid using wrong (deprecated) keys in case an old source with the same name
                # existed.
                self._source_id = rest.getSourceID(self._serverURL, self._conf['headers'], self._account, sourceName)
                acc_token = False if self._token == '' else self._token
                self._credentials = rest.getSourceKey(self._serverURL, self._conf['headers'], sourceName, token=acc_token)
                self._source = sourceName
                self._source_credentials.update({sourceName: [ self._credentials, self._source_id ]})
                self.__updateSourceFile()
                vis = rest.getSourceById(self._serverURL, self._conf['headers'], self._source_id)
                if vis:
                    self._source_charts = [v['name'] for v in vis['visualizations']]
                    self.__updateSourceFile()
        else:
            print('You need to authenticate: ZD.auth("user","password")')

    def sources(self):
        """ List the availables sources for the account"""
        if(self._conf['headers']['Authorization']):
            rest.getSourcesByAccount(self._serverURL, self._conf['headers'], self._account)
        else:
            print('You need to authenticate: ZD.auth("user","password")')

    def __getVisualization(self):
        # Request the source key in case it does not exists, this will allow to 
        # render the visualization if the notebook is re-opened
        params = { 'conf': self._conf,
                   'credentials': self._credentials,
                   'token': self._token,
                   'paths': self._paths,
                   'width': self._width,
                   'height': self._height,
                   'source': self._source,
                   'chart': self._chart,
                   'query': self._query,
                   'filters': self._filters,
                   'variables': self._variables }
        vr = VisRender(params)
        return vr.getVisualization(self._renderCount, self._pickers)

    def __render(self, pickers, filters):
        if(self._source):
            self._pickers = pickers
            self._filters = filters
            iframe = self.__getVisualization()[0]
            self._renderCount += 1
            return HTML(iframe)
        else:
            print('You need to specify a source: ZD.source = "Source Name"')

    def graph(self, src="", chart= "", conf={}, filters={}):
        """ Renders a visualization from Zoomdata. Takes in count the ZD object attributes such as
        chart, source, etc. to render an specific visualization. 
            - Parameters:
            source: String. Specify the source of the visualization
            chart: String. Specify what type of visualization will be rendered
            conf: Dictionary (optional). Defaults values for the the pickers (attribute/metric). 
                  This attribute is different depending on the chart type. Ex:

                  For: Bars, Donut, Floating Bubbles, Pie, Tree Map, Packed Bubbles, Word Cloud
                  {'attribute':'Ticket', 'metric': 'Survived', 'operation':'sum', 'limit':10 }

                  For: KPI
                  {'metric': 'Survived', 'operation':'sum'}

                  For Line & Bars Trend
                  {'y1':'Commision', 'y2':'Pricepaid', 'op1': 'sum', 'op2':'avg', 'trend':'Saletime','unit':'MONTH', 'limit':10 }

                  For Line Trend: Attribute Values
                  {'attribute':'Ticket', 'metric':'Pricepaid', 'operation': 'sum', 'trend':'Saletime','unit':'MONTH', 'limit':10 }

                  For Map: Markers no attributes are required

            filters: List of dictionaries: Each dictionary must contain the name of the field to be used as a filter and a list
                of values that the data must match. The name of the fields can be obtained through ZD.fields()
                Ex: {'field1':['value1','value2'], 'field2':'value1'}

        """
        if(self.setSource(src)):
            if(self.__setChart(chart)):
                return self.__render(conf, filters)

    # ==== Graph shorcut methods =============

    def pie(self, filters={}, **conf):
        """
        Renders a Pie visualization for the default source if defined. 
        Parameters:
            Set of optional attributes to use as default: 
            - filters: List of dictionaries: Each dictionary must contain the name of the field to be used as a filter and 
                a list of values that the data must match. The name of the fields can be obtained through ZD.fields()
                Ex: {'field1':['value1','value2'], 'field2':'value1'}
            - attribute: String. Field name to use as default attribute/dimension
            - metric: String. Field name to use as default metric
            - limit: Integer: Max number of results
            - operation: The type of the operation/function on the metric. sum/max/min/avg
        """
        return self.graph(self._source, 'Pie', conf, filters)

    def bars(self, filters={}, **conf):
        """
        Renders a bars visualization for the default source if defined. 
        Parameters:
            Set of optional attributes to use as default: 
            - filters: List of dictionaries: Each dictionary must contain the name of the field to be used as a filter and 
                a list of values that the data must match. The name of the fields can be obtained through ZD.fields()
                Ex: {'field1':['value1','value2'], 'field2':'value1'}
            - attribute: String. Field name to use as default attribute/dimension
            - metric: String. Field name to use as default metric
            - limit: Integer: Max number of results
            - operation: The type of the operation/function on the metric. sum/max/min/avg
        """
        return self.graph(self._source, 'Bars', conf, filters)

    def donut(self, filters={}, **conf):
        """
        Renders a Donut visualization for the default source if defined. 
        Parameters:
            Set of optional attributes to use as default: 
            - filters: List of dictionaries: Each dictionary must contain the name of the field to be used as a filter and 
                a list of values that the data must match. The name of the fields can be obtained through ZD.fields()
                Ex: {'field1':['value1','value2'], 'field2':'value1'}
            - attribute: String. Field name to use as default attribute/dimension
            - metric: String. Field name to use as default metric
            - limit: Integer: Max number of results
            - operation: The type of the operation/function on the metric. sum/max/min/avg
        """
        return self.graph(self._source, 'Donut', conf, filters)

    def heatMap(self, filters={}, **conf):
        """
        Renders a Heat Map  visualization for the default source if defined. 
        Parameters:
            Set of optional attributes to use as default (if supported): 
            - filters: List of dictionaries: Each dictionary must contain the name of the field to be used as a filter and 
                a list of values that the data must match. The name of the fields can be obtained through ZD.fields()
                Ex: {'field1':['value1','value2'], 'field2':'value1'}
            - attribute: String. Field name to use as default attribute/dimension
            - metric: String. Field name to use as default metric
            - limit: Integer: Max number of results
            - operation: The type of the operation/function on the metric. sum/max/min/avg
        """
        return self.graph(self._source, 'Heat Map', conf, filters)

    def mapMarkers(self, filters={}, **conf):
        """
        Renders a Map: Markers visualization for the default source if defined. 
        This type of chart must be supported by the source
        """
        return self.graph(self._source, 'Map: Markers', conf, filters)

    def kpi(self, filters={}, **conf):
        """
        Renders a KPI visualization for the default source if defined. 
        Parameters:
            Set of optional attributes to use as default (if supported): 
            - filters: List of dictionaries: Each dictionary must contain the name of the field to be used as a filter and 
                a list of values that the data must match. The name of the fields can be obtained through ZD.fields()
                Ex: {'field1':['value1','value2'], 'field2':'value1'}
            - metric: String. Field name to use as default metric
            - operation: The type of the operation/function on the metric. sum/max/min/avg
        """
        return self.graph(self._source, 'KPI', conf, filters)

    def treeMap(self, filters={}, **conf):
        """
        Renders a Tree Map  visualization for the default source if defined. 
        Parameters:
            Set of optional attributes to use as default (if supported): 
            - filters: List of dictionaries: Each dictionary must contain the name of the field to be used as a filter and 
                a list of values that the data must match. The name of the fields can be obtained through ZD.fields()
                Ex: {'field1':['value1','value2'], 'field2':'value1'}
            - attribute: String. Field name to use as default attribute/dimension
            - metric: String. Field name to use as default metric
            - limit: Integer: Max number of results
            - operation: The type of the operation/function on the metric. sum/max/min/avg
        """
        return self.graph(self._source, 'Tree Map', conf, filters)

    def __getHTML(self):
        try:
            import jsbeautifier
            from bs4 import BeautifulSoup as bs
            iframe, html, jscode = self.__getVisualization()
            soup=bs(html,"lxml")
            html=soup.prettify()
            jscode = jsbeautifier.beautify(jscode)
            print (html+'\n'+jscode)
        except ImportError:
            print ('Modules jsbeautifier and beautifulsoup4 are required for this feature')

    def getConnectionData(self, sourceName=False):
        """
        Return the connection parameters for a given source. If not source is specified the parameters
        of the current source will be shown
        """
        source_id = self._source_id
        if sourceName:
            print('Retrieving specified source...')
            source_id = rest.getSourceID(self._serverURL, self._conf['headers'], self._account, sourceName)
        if source_id:
            print('Fetching source parameters...')
            vis = rest.getSourceById(self._serverURL, self._conf['headers'], source_id)
            if vis:
                print('')
                print('Name : '+vis['name'])
                print('ID : '+source_id)
                print('Storage: '+vis['type'])
                for key in vis['storageConfiguration']:
                    print(key+': '+str(vis['storageConfiguration'][key]))
        else:
            print('You must specify a source')

    def fields(self, sourceName=False, conf={}):
        """
        Retrieve or modify the fields for a given source. It takes to optional parameters:
            - sourceName: String: Set the source from where fields will be fetched/modified. If no source is specified
                          the current source will be used
            - conf: Dictionary: The new configuration for the fields using field name as key. Ex:
                        {'field_name1':{'type':'new_type','visible':True, 'label':'New Label'}, {'field_name2':...}}}
                        If no conf is specified, the current fields conf will be retrieved.
        """
        source_id = self._source_id
        if sourceName:
            print('Retrieving specified source...')
            source_id = rest.getSourceID(self._serverURL, self._conf['headers'], self._account, sourceName)
        if source_id:
            print('Fetching source fields...')
            vis = rest.getSourceById(self._serverURL, self._conf['headers'], source_id)
            if vis and not conf: # Only print the attrs config. No update
                print('')
                for f in vis['objectFields']:
                    val = "%s: {'label':'%s', 'type':'%s', 'visible':%s }" \
                            % (f['name'], f['label'], f['type'], f['visible'])
                    print(val)
            elif vis and conf: #Do not print, just update
                fields = [f for f in conf.keys()]
                for f in vis['objectFields']:
                    if f['name'] in conf:
                        for key in conf[f['name']].keys():
                            if key in f: # Check if the key is in the original, to avoid inserting wrong keys
                                f[key] = conf[f['name']][key]
                print('Updating source fields...')
                if(rest.updateSourceDefinition(self._serverURL, self._conf['headers'], source_id, vis)):
                    print('Done')
        else:
            print('You must specify a source')


    #====== SET CHART TYPES FOR A VISUALIZATION IF IT DOES NOT HAVE IT ==========
    def setVisualization(self, name, definition={}):
        if(self._conf['headers']['Authorization']):
            # 1. First get the ID of the specific visualization
            if self._credentials:
                print('Checking allowed chart types...')
                if not (self._allowed_visuals):
                    self._allowed_visuals = rest.getVisualizationsList(self._serverURL, self._conf['headers'])
                visualsNames = [v['name'] for v in self._allowed_visuals]
                if name not in visualsNames:
                    print('Visualization type not found or not configured. Supported visualizations are:')
                    print('\n'.join(visualsNames))
                else:
                    visId = [v['id'] for v in self._allowed_visuals if v['name'] == name]
                    result = False
                    if name == 'Map: Markers':
                        result = vd.setMapMarkers(visId[0], definition, self._serverURL, \
                                                    self._conf['headers'], self._source_id)
                    elif name == 'Line & Bars Trend':
                        result = vd.setLineBarsTrend(visId[0], definition, self._serverURL, \
                                                    self._conf['headers'], self._source_id)
                    if result:
                        self._source_charts.append(name)
                    else:
                        print('There where error or perhaps the add/update feature is not supported yet for this chart')

            else:
                print('You must define a source before setting a new visualization')
        else:
            print('You need to authenticate: ZD.auth("user","password")')

            
    def __setChart(self, nchart):
        if(self._conf['headers']['Authorization']):
            # If the graph() function is called using the same source and chart, there is no need
            # to change it
            if (not nchart and self._chart) or (nchart == self._chart): 
                return True
            if not self._source:
                print('You need to define a source before setting the chart')
            else:
                if not self._allowed_visuals:
                    self._allowed_visuals = rest.getVisualizationsList(self._serverURL, self._conf['headers'])
                visualsNames = [v['name'] for v in self._allowed_visuals]
                if nchart in visualsNames: # If is an allowed visualization type
                    if nchart in self._source_charts: # If is an active visualization for the source
                        self._chart = nchart
                        return True
                    else:
                        print('Chart type not configured, to configure it use ZD.setVisualization method')
                else:
                    print('Chart type not found. Supported charts are:')
                    print('\n'.join(visualsNames))
        else:
            print('You need to authenticate: ZD.auth("user","password")')
        return False

    def setSource(self, nsource):
        """
        Allows to manually set up a new source for different operations just as fields() or getConnectionData()
        Parameters:
            - source: (String). The name of the source
        """
        #Set the source
        if (not nsource and self._source) or (nsource == self._source): 
            return True
        if(self._conf['headers']['Authorization']):
            #To avoid useless requests, check the local env to see if the source is registered
            credentials = False
            source_id = False
            if self._source_credentials.get(nsource, False): # If the source is allready registered
                credentials = self._source_credentials[nsource][0] # The key of the source
                source_id = self._source_credentials[nsource][1] # The id of the source
            else:
                source_id = rest.getSourceID(self._serverURL, self._conf['headers'], self._account, nsource)

            if not credentials: 
                acc_token = False if self._token == '' else self._token
                credentials = rest.getSourceKey(self._serverURL, self._conf['headers'], nsource, token=acc_token)
                if not credentials:
                    print('Some problems were found trying to set up this source, perhaps it was deleted from Zoomdata')
                    return False
            self._source = nsource
            self._credentials = credentials
            self._source_id = source_id
            self._source_credentials.update({nsource: [ self._credentials, self._source_id ]})
            vis = rest.getSourceById(self._serverURL, self._conf['headers'], self._source_id)
            if vis:
                self._source_charts = [v['name'] for v in vis['visualizations']]
                self.__updateSourceFile()
                return True
            else: # If not vis it means that source was deleted from zoomdata
                self._source_credentials.pop(nsource)
                self.__updateSourceFile()
                print('Some problems were found trying to set up this source, perhaps it was deleted from Zoomdata')
                return False 

        else:
            print('You need to authenticate: ZD.auth("user","password")')
            return False



    #====== PROPERTIES (DEFINED THIS WAY TO PROVIDE DOCSTRING) ===============
    @property
    def conf(self):
        """Dict: Configuration to create collections and sources. Uses specific Zoomdata configuration such as port and server for mongo connections, accounts Ids, authorization headers
        """
        return self._conf

    @conf.setter
    def conf(self, value):
        self._conf = value
        protocol = 'https' if self._conf['secure'] else 'http'
        self._serverURL = '%s://%s:%s%s' % (protocol, self._conf['host'], self._conf['port'], self._conf['path'])

    def first(self, source, fields=[], filters=[]):
        """
        Retrieve the first data row from the specified source as a pandas dataframe object.
        Parameters:
            - source: String. The name of the source.
            - fields: List (optional). A list with the name of the fields. The fetched data will be restricted only to these fields. All fields will be returned if no fields list is specified.
            - filters: List of dicts (optional). A list of filters for the requested data. Ex:
                filters = [{'path':'fieldname','operation':'IN', 'value':['value1','value2']},{...}]
        """
        return self.getData(source, fields=fields, rows=1, filters=filters)


    def getData(self, source, fields=[], rows=10000, filters=[]):
        """
        Retrieve data from the specified source as a pandas dataframe object.
        Parameters:
            - source: String. The name of the source.
            - fields: List (optional). A list with the name of the fields. The fetched data will be restricted only to these fields. All fields will be returned if no fields list is specified.
            - rows: Integer (optional). The limit of rows fetched. Default is 10,000. Top limit is 1,000,000.
            - filters: List of dicts (optional). A list of filters for the requested data. Ex:
                filters = [{'path':'fieldname','operation':'IN', 'value':['value1','value2']},{...}]
        """
        return self.__getWebsocketData(source, fields=fields, rows=rows, filters=filters)

    def getVisualData(self, source, conf, filters=[]):
        """
        Returns the aggregated data (data used for an specific visualization) for a given source.
        Parameters:
            - source. String. The name of the source.
            - conf. Dictionary. The configuration to fetch the aggregated data.
                conf = {"fields": [{"name": "hotel_name", "limit": 20, "sort": {"dir": "desc", "name": "count"}}], "metrics": [{"func": "count", "name": "*"}]}
            - filters: List of dicts (optional). A list of filters for the aggregated data. Ex:
                filters = [{'path':'fieldname','operation':'IN', 'value':['value1','value2']},{...}]
        """
        if not conf or not isinstance(conf,(dict)):
            print("The configuration parameter is required, and it has to be a python dict")
            return False
        return self.__getWebsocketData(source, visual=True, config=conf, filters=filters)

    def __getWebsocketData(self, source, visual=False, fields=[], rows=10000, config={}, filters=[]):
        try:
            import ssl
            from websocket import create_connection
            credentials = ''
            source_id = ''
            if self._source_credentials.get(source, False): # If the source is allready registered
                credentials = self._source_credentials[source][0] # The key of the source
                source_id = self._source_credentials[source][1] # The id of the source
            else:
                if(self._conf['headers']['Authorization']):
                    source_id = rest.getSourceID(self._serverURL, self._conf['headers'], self._account, source)
                else:
                    print('You need to authenticate: ZD.auth("user","password")')
                    return False

            if not credentials:
                acc_token = False if self._token == '' else self._token
                credentials = rest.getSourceKey(self._serverURL, self._conf['headers'], source, token=acc_token)
                if not credentials:
                    return False
                self._source_credentials.update({source: [ credentials, source_id ]})
                self.__updateSourceFile()
 
            # Parse the fields in case they are for the not visual
            if not fields and not visual:
                vis = rest.getSourceById(self._serverURL, self._conf['headers'], source_id)
                if vis:
                    fields = [f['name'] for f in vis['objectFields']]
                else:    
                    return False
            # Websocket request
            socketUrl = self._serverURL + "/websocket?key=" + credentials
            socketUrl = socketUrl.replace('https','wss')
            ws = create_connection(socketUrl)
            rows = rows if rows < 1000000 else 1000000
            request = { "type": "START_VIS",
                        "cid": "f3020fa6e9339ee5829f6e2caa8d2e40",
                        "request": {
                               "streamSourceId": source_id,
                               "cfg": {}
                            }
                     }
            if not visual:
                conf = {'tz':'EST', 'fields':fields, 'limit':rows, 'filters':filters}
            else:
                conf = {"filters":filters, "group": config}
                #request['request'].update({'time':{'timeField':'_ts'}})
            request['request']['cfg'].update(conf)
            ws.send(js.s(request))
            req_done = False
            dataframe = []
            maxloop = 0
            while maxloop <= 30:
                frame = ws.recv() #NOTE: This will hang if no data is received
                if 'NOT_DIRTY_DATA' in frame:
                    ws.close()
                    break
                maxloop += 1
                frame = frame.replace('false','False')
                frame = frame.replace('null','None')
                frame = eval(frame)
                dataframe.extend(frame.get('data',[]))

            #Parsing takes a little more due to they're different for each visuals
            if maxloop == 30: # There was an error
                ws.close()

            if dataframe:
                if visual: 
                    dfParsed = []
                    columns = []
                    fields = [f['name'] for f in config['fields']]
                    opKeys = ['sum','avg','max','min']
                    attrName = 'category'
                    for obj in dataframe:
                        row = []
                        for attr in obj['group']:
                            row.append(attr)
                        metrics = obj['current'].get('metrics',False)
                        if metrics:
                            for m in  metrics:
                                for op in opKeys:
                                    if metrics[m].get(op, False):
                                        row.append(metrics[m][op])
                                        metricName = '%s(%s)' % (m, op)
                                        if metricName not in fields:
                                            fields.append(metricName)
                        if obj['current'].get('count', False):
                            row.append(obj['current']['count'])
                            if 'count' not in fields:
                                fields.append('count')
                        dfParsed.append(row)
                    dataframe = dfParsed
                if fields:
                    return pd.DataFrame(dataframe, columns=fields)
                return pd.DataFrame(dataframe)
            print('No data was returned')
            return False

        except ImportError:
            print ('No websocket module found. Install: pip3 install websocket-client')

