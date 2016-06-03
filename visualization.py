#/usr/bin/python3
from .config import *
from .jsbuilder import JSBuilder
from .templates import Template
from IPython.display import HTML
import os
js = JSBuilder()
t = Template()

class ZDVisualization(object):

    """ ZDVisualization puts together all the javascript pieces
    needed to create a connection with the ZD SDK and fecth 
    the requested data. It finally renders the html and js into
    the notebook output dom through the HTML object """

    def __init__(self):
        """ To ensure maximum flexibility for the visualization configuration
        here must be setted all values that may change """
        self.width = 800
        self.height = 400
        self.renderCount = 0 #To render a different chart each time
        self.paths = paths
        self.appConfig = applicationConfig
        self.query = queryConfig
        self.credentials =credentials
        self.source = source
        self.chart = chart
        self.variables = {}
        self.metric = metric
        self.group = groups
        self.filters = []
        self.metricParams = metricParams
        self.groupParams = groupParams

    def __setRequireConf(self):
        #Set the require configuration part
        return 'require.config({paths:%s});' % js.s(self.paths)

    def __getJSTools(self):
        tools = ''
        path = os.path.dirname(os.path.realpath(__file__))
        with open(path+'/tools.js') as t: #Set of functions used within the script
            tools = ''.join(t.readlines())
        return tools

    def __getFilters(self):
        opt = t.optionFmt % ('','Select option')
        dim = t.selectFmt % ('Dimension', self.groupParams['name'], opt)
        met = t.selectFmt % ('Metric', self.metricParams['name'], opt)
        return t.divFilters % (dim + met)

    def __createClient(self):
        credentials = {
                'credentials': {'key': self.credentials},
                'application': self.appConfig,
                }
        params = js.s(credentials)
        return 'ZoomdataSDK.createClient(%s)' % (params)

    def __connectionPromise(self):
        """Returns the string associated to the 
        promise that connects with ZD and creates the visualization"""
        prom = self.__createClient()
        p ='window.client = client; return(client)'
        then = '.then(%s)' % (js.createFunc(params='client',body=p, anon=True))
        visualconf = {'element':'%s', 'config': self.query}
        visualconf.update( { 'source': {'name': self.source},
                             'visualization': self.chart,
                             'variables': self.variables
                           })
        p = js.s(visualconf)
        p = js.setVars(p, 'visLocation') #set the element for echarts rendering

        # The function .done is where the Thread object is created
        # and the specific data such as groups, variables, parameters,
        # etc for the specific visualization being loaded
        doneBody = t.doneBody % {'met': self.metricParams['name'], 'dim': self.groupParams['name'] }
        done = '.done(%s);' % (js.createFunc(params='result',body=doneBody, anon=True))
        p = 'client.visualize(%s)%s' % (p, done)
        then1 = '.then(%s);' % (js.createFunc(params='client',body=p, anon=True))
        return prom+then+then1

    def __wrapper(self):
        """Wraps and render all the JS code inside the require module"""
        deps = ['ZoomdataSDK','jquery']
        tools = self.__getJSTools()
        visualDiv = 'visual%s' % (str(self.renderCount))
        varKernel = js.var('kernel','IPython.notebook.kernel')
        varChart = js.var('chart',js.s(self.chart))
        groupAccessor = js.var('groupAccessor',js.s(self.groupParams['attr']))
        metricAccessor = js.var('metricAccessor',js.s(self.metricParams['attr']))
        visLocation = js.var('visLocation','document.getElementById("'+visualDiv+'")')
        varFilters  = js.var('filters', '[]')
        #These two variables hold the selected metric and dimensions objects
        varMetric   = js.var(self.metricParams['name'], js.s(self.metric))
        varGroup    = js.var(self.groupParams['name'], js.s(self.group))
        #The promise with the SDK connection code
        zdSDK = self.__connectionPromise()
        #. Jquery onchange handlers for the filters
        metricJS = t.metricFilter % self.metricParams
        dimensionJS = t.groupFilter %  self.groupParams
        # wrap everything up as the require callback body
        cb = tools + visLocation + varFilters + varChart \
            + groupAccessor + metricAccessor + varMetric \
            + varGroup + zdSDK + metricJS + dimensionJS
        reqCallback = js.createFunc(params=deps, body=cb, anon=True)
        return 'require(%s,%s)' % (js.s(deps), reqCallback)

    def __getVisualization(self):
        """Set up of the final code snippet to be rendered"""
        w, h = self.width, self.height
        visualDiv = 'visual%s' % (str(self.renderCount))
        filters = self.__getFilters()
        htmlcode = filters + t.divChart % (visualDiv, str(w), str(h))
        jscode = t.scriptTags % (self.__setRequireConf(), self.__wrapper())
        html = htmlcode + jscode
        iframe = t.iframe % (t.requirejs, html, str(w+40), str(h+50) )
        return iframe, htmlcode, jscode

    def render(self):
        iframe = self.__getVisualization()[0]
        self.renderCount += 1
        return HTML(iframe)
        # return HTML(html + jscode)

    def getHTML(self):
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







        
