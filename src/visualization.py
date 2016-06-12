#/usr/bin/python3
import os
import urllib3
import json
import base64
from .rest import RestCalls
from .visdefinition import VisDefinition
from .config import *
from .jsbuilder import JSBuilder
from .templates import Template
from IPython.display import HTML

http = urllib3.PoolManager()
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
        self._account = ''
        if os.path.exists('data/sources.json'):
            with open('data/sources.json','r') as sc:
                self._source_credentials = json.load(sc)

        self.notebook = ''

        #Visualization attrs
        self.connResp = {}
        self._width = 800
        self._height = 400
        self._renderCount = 0 #To render a different chart each time
        self._paths = paths
        self._query = queryConfig
        self._credentials = ''  # This is the key to get the source key to get the visualization
        self._source_id = '' # This is the source id to get the source definition
        self._source_charts = [] # Active visualizations for the current source
        self._allowed_visuals = [] # All the visualizations names allowed by zoomdata
        self._source = ''
        self._chart = chart
        self._variables = {}
        self._metric = metric
        self.test = ''
        self._group = groups
        self._filters = []

        #Attrs for new source/collection creation
        self._connReq = connReq
        self._sourceReq = sourceReq

    def auth(self, user, password):
        cred = user+':'+password
        key = base64.b64encode(cred.encode('ascii'))
        key = 'Basic ' + key.decode('ascii')
        self._connReq['mongo']['created']['by']['username'] = user
        self._sourceReq['created']['by']['username'] = user
        self._conf['headers']['Authorization'] = key
        # Get the account
        self._account = rest.getUserAccount(self._serverURL, self._conf['headers'], user)

    def __createMongoCollection(self, name, df, connName):
        """ Creates a MongoDB collection """
        try:
            from pymongo import MongoClient
            client = MongoClient(self._conf['mongoServer'], self._conf['mongoPort'] )
            db = getattr(client, self._conf["mongoSchema"])
            collection = db[name] 
            if df: # Use the dataframe if it is specified
                print('Creating collection '+name+'...')
                collection.insert_many(df)
                print('collection created on db')
            print('creating data source using collection '+name+'...')
            return rest.createSource(self._serverURL, self._conf['headers'], \
                                     self._account, name, connName, 
                                     self._connReq, self._sourceReq)
        except ImportError:
            print ('To create mongo collections you must have the pymongo module installed')
        except Exception as e:
            print('Error: '+str(e))

    def createSource(self, sourceName, dataframe=False, handler='mongo', connName=False): 
        """Creates a new Zoomdata collection using the specified parameters:
                Parameters:
                    sourceName: The name given for the new source
                    dataframe: Contains the data used to populate the source, if it is not specified
                               then a collection with name sourceName will be used instead
                    handler: The store handler, 'mongo' is used by default
                    connName: The name of the connection, if no name is specified, the source name will be used.
        """
        if(self._conf['headers']['Authorization']):
            if handler in ['mongo','spark']:
                if handler == 'mongo':
                    connName = connName or sourceName
                    return self.__createMongoCollection(sourceName, dataframe, connName)
            else:
                print('Invalid collection handler!')
        else:
            print('You need to authenticate: ZD.auth("user","password")')

    def listSources(self):
        """ List the availables sources for the account"""
        if(self._conf['headers']['Authorization']):
            rest.getSourcesByAccount(self._serverURL, self._conf['headers'], self._account)
        else:
            print('You need to authenticate: ZD.auth("user","password")')
            
    def __setRequireConf(self):
        #Set the require configuration part
        return 'require.config({paths:%s});' % js.s(self._paths)

    def __getJSTools(self):
        tools = ''
        path = os.path.dirname(os.path.realpath(__file__))
        with open(path+'/js/tools.js') as t: #Set of functions used within the script
            tools = ''.join(t.readlines())
        return tools

    def __getPickers(self):
        opt = t.optionFmt % ('','Select option')

        #Options for the metric operators picker
        oper  = t.optionFmt % ('min','Min')
        oper += t.optionFmt % ('max','Max')
        oper += t.optionFmt % ('sum','Sum')
        oper += t.optionFmt % ('avg','Avg')
        #Include the count/volume in the metrics
        count = t.optionFmt % ('count','Count')

        pickers = ""
        if self._chart not in ["Line & Bars Trend"]:
            pickers = t.selectFmt % ('grp-span','Dimension', 'group', opt)
            pickers += t.selectFmt % ('met-span','Metric', 'metric1', opt+count)
        else:
            pickers = t.selectFmt % ('met-span','Y1 Axis', 'metric1', opt+count)
            pickers += t.selectFmt % ('met-span','Y2 Axis', 'metric2', opt+count)
        pickers += t.selectFmt % ('op-span','Operation', 'func' , opt+oper)
        return t.divFilters % (pickers)

    def __createClient(self):
        credentials = {
                'credentials': {'key': self._credentials},
                'application': {'secure': self._conf['secure'], 
                                'host': self._conf['host'], 
                                'port': self._conf['port'], 
                                'path': self._conf['path']}
                }
        params = js.s(credentials)
        return 'ZoomdataSDK.createClient(%s)' % (params)

    def __connectionPromise(self):
        """Returns the string associated to the 
        promise that connects with ZD and creates the visualization"""
        prom = self.__createClient()
        p ='window.client = client; return(client)'
        then = '.then(%s)' % (js.createFunc(params='client',body=p, anon=True))
        visualconf = {'element':'%s', 'config': self._query}
        visualconf.update( { 'source': {'name': self._source},
                             'visualization': self._chart,
                             'variables': '%s' #Initialization variables
                           })
        p = js.s(visualconf)
        p = js.setVars(p, ('visLocation','variables')) #set the element for echarts rendering

        # The function .done is where the Thread object is created
        # and the specific data such as groups, variables, parameters,
        # etc for the specific visualization being loaded
        done = '.done(%s);' % (js.createFunc(params='result',body=t.doneBody, anon=True))
        test = 'console.log("Heeey Im here");'
        p = 'client.visualize(%s)%s' % (p, done)
        p = test + p
        then1 = '.then(%s);' % (js.createFunc(params='client',body=p, anon=True))
        return prom+then+then1

    def __wrapper(self):
        """Wraps and render all the JS code inside the require module"""
        tools = self.__getJSTools()
        visualDiv = 'visual%s' % (str(self._renderCount))
        varChart = js.var('chart',js.s(self._chart))
        visLocation = js.var('visLocation','document.getElementById("'+visualDiv+'")')
        varFilters  = js.var('filters', '[]')
        varVariables= js.var('variables', js.s(self._variables))
        # These vars hold the selected dataAccessor
        varMetricAccessor  = js.var('metricAccessor', '""')
        varGroupAccessor  = js.var('groupAccessor', '""')
        # These var hold the selected metric operator 
        varOperator = js.var('metricOp','""')
        #These two variables hold the selected metric and dimensions objects
        varMetric   = js.var('metric', js.s(self._metric))
        varGroup    = js.var('group', js.s(self._group))
        # The kernel variable to communicate python-js
        varKernel   = js.var('kernel', 'Ipython.notebook.kernel')
        #The promise with the SDK connection code
        zdSDK = self.__connectionPromise()
        #. Jquery onchange handlers for the pickers
        pickersJS = ""
        if self._chart not in ["Line & Bars Trend"]:
            pickersJS = t.groupPicker 
            pickersJS += t.metricPicker % {'metID':'metric1'}
        else:
            pickersJS = t.metricPicker % {'metID':'metric1'}
            pickersJS += t.metricPicker % {'metID': 'metric2'}
        pickersJS += t.funcPicker 
        # wrap everything up as the require callback body
        cb = tools + visLocation + varVariables + varFilters + varChart + varMetric \
            + varGroup + varOperator + zdSDK + pickersJS
        reqCallback = js.createFunc(params=deps, body=cb, anon=True)
        return 'require(%s,%s)' % (js.s(deps), reqCallback)

    def __getVisualization(self):
        """Set up of the final code snippet to be rendered"""
        w, h = self._width, self._height
        visualDiv = 'visual%s' % (str(self._renderCount))
        pickers = ''
        if self._chart not in ['Map: Markers']:
            pickers = self.__getPickers()
        htmlcode = pickers + t.loadmsg + t.divChart % (visualDiv, str(w), str(h))
        jscode = t.scriptTags % (self.__setRequireConf(), self.__wrapper())
        html = htmlcode + jscode
        iframe = t.iframe % (t.requirejs, html, str(w+40), str(h+80) )
        return iframe, htmlcode, jscode

    def render(self):
        """ Renders a visualization from Zoomdata. Takes in count the ZD object attributes such as
        chart, source, etc. to render an specific visualization """
        if(self._source):
            iframe = self.__getVisualization()[0]
            self._renderCount += 1
            return HTML(iframe)
        else:
            print('You need to specify a source: ZD.source = "Source Name"')
        # return HTML(html + jscode)

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
                print('mongo host: '+self._conf['mongoServer'])
                print('mongo port: '+ str(self._conf['mongoPort']))
                for key in vis['storageConfiguration']:
                    print(key+': '+str(vis['storageConfiguration'][key]))
        else:
            print('You must specify a source')

    def sourceFields(self, sourceName=False, conf={}):
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
                    result = vd.setMapMarkers(visId[0], definition, self._serverURL, \
                                                self._conf['headers'], self._source_id)
                    if result:
                        self._source_charts.append(name)
            else:
                print('You must define a source before setting a new visualization')
        else:
            print('You need to authenticate: ZD.auth("user","password")')

    def __getNotebookPath(self):
        jscode = """
                <script type='text/javascript'>
                var nb = IPython.notebook;
                var kernel = IPython.notebook.kernel;
                var command = "ZD.notebook = '" + nb.base_url + nb.notebook_path + "'";
                kernel.execute(command);
                </script>
        """
        return HTML(jscode)

            
    #====== PROPERTIES (DEFINED THIS WAY TO PROVIDE DOCSTRING) ===============
    @property
    def chart(self):
        """String: The chart types for the visualization. Allowed values are:
            Donut, Bars, Pie, KPI, Scatter Plot, Floating Bubbles, Packed Bubbles,
            Tree Map, Heat Map, Word Cloud
        """
        return self._chart

    @chart.setter
    def chart(self, value):
        if(self._conf['headers']['Authorization']):
            if not self._source:
                print('You need to define a source before setting the chart')
            else:
                if not (self._allowed_visuals):
                    self._allowed_visuals = rest.getVisualizationsList(self._serverURL, self._conf['headers'])
                visualsNames = [v['name'] for v in self._allowed_visuals]
                if value in visualsNames: # If is an allowed visualization type
                    if value in self._source_charts: # If is an active visualization for the source
                        self._chart = value
                    else:
                        print('Chart type not configured, to configure it use ZD.setVisualization method')
                else:
                    print('Chart type not found. Supported charts are:')
                    print('\n'.join(visualsNames))
        else:
            print('You need to authenticate: ZD.auth("user","password")')

    @property
    def width(self):
        """ Integer: The width of the visualization """
        return self._width

    @width.setter
    def width(self, value):
        self._width = value

    @property
    def height(self):
        """ Integer: The height of the visualization """
        return self._height

    @height.setter
    def height(self, value):
        self._height = value

    # @property
    # def paths(self):
        # return self._paths

    # @paths.setter
    # def paths(self, value):
        # self._paths = value

    @property
    def query(self):
        """
        Dictionary. Allows to manually modify the query used to fecth data from ZD. 
        """
        return self._query

    @query.setter
    def query(self, value):
        self._query = value

    @property
    def source(self):
        """ The source used to fetch and render the visualization """
        return self._source

    @source.setter
    def source(self, value):
        credentials = ''
        if(self._conf['headers']['Authorization']):
            #This will change once oauth is implemented, cuz the key won't be needed anymore
            self._credentials = rest.getSourceKey(self._serverURL, self._conf['headers'], value)
            if self._credentials:
                self._source = value
                self._source_id = rest.getSourceID(self._serverURL, self._conf['headers'], self._account, value)
                self._source_credentials.update({value: [ self._credentials, self._source_id ]})
                if not self._source_charts:
                    vis = rest.getSourceById(self._serverURL, self._conf['headers'], self._source_id)
                    self._source_charts = [v['name'] for v in vis['visualizations']]
                with open('data/sources.json', 'w') as sc:
                    json.dump(self._source_credentials, sc)
            else:
                print('You need to authenticate: ZD.auth("user","password")')

    @property
    def variables(self):
        """ String: Representation of a JSON """
        return self._variables

    @variables.setter
    def variables(self, value):
        self._variables = value

    @property
    def metric(self):
        """ Dict: Represent the metric used to render the visualization. Can be visually changed through drop-downs"""
        return self._metric

    @metric.setter
    def metric(self, value):
        self._metric = value

    @property
    def group(self):
        """ Dict: Represent the dimension used to render the visualization. Can be visually changed through drop-downs"""
        return self._group

    @group.setter
    def group(self, value):
        self._group = value

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

    @property
    def connReq(self):
        """ Dict: Specific data for store handlers as mongo, spark, etc. """
        return self._connReq

    @connReq.setter
    def connReq(self, value):
        self._connReq = value

    @property
    def sourceReq(self):
        """
        Dict Specific data for source creation. Allows to add description to the source being created.
        """
        return self._sourceReq

    @sourceReq.setter
    def sourceReq(self, value):
        self._sourceReq = value




        
