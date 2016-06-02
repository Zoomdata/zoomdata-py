#/usr/bin/python3
from .config import *
from .jsbuilder import JSBuilder
from .templates import Template
from IPython.display import HTML
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
        self.metricParams = metricParams
        self.groupParams = groupParams

    def __setRequireConf(self):
        #Set the require configuration part
        return 'require.config({paths:%s});' % js.s(self.paths)

    def __createFilterSelect(self, name='', options=[]):
        '''Wraps a list of strings (options) as an html select'''
        opts = ''
        if isinstance(options,(str)):
            options = eval(options)
        for o in options:
            opts += t.optionFmt % (o,o)
        return t.selectFmt % (name, name.lower(), opts)

    def __getFilters(self):
        dimensions = ["category", "group", "sku", "usergender", "usercity", "userstate", "zipcode", "$to_day(_ts)"] 
        metrics = ["price", "plannedsales", "usersentiment"]
        dim = self.__createFilterSelect('Dimension', dimensions)
        met = self.__createFilterSelect('Metric', metrics)
        return t.divFilters % (dim + met)

    def __createClient(self):
        credentials = {
                'credentials': self.credentials,
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
        done = '.done(%s);' % (js.createFunc(params='result',body='window.viz = result', anon=True))
        p = 'client.visualize(%s)%s' % (p, done)
        then1 = '.then(%s);' % (js.createFunc(params='client',body=p, anon=True))
        return prom+then+then1

    def __wrapper(self):
        """Wraps and render all the JS code inside the require module"""
        deps = ['ZoomdataSDK','jquery']
        visualDiv = 'visual%s' % (str(self.renderCount))
        visLocation = js.var('visLocation','document.getElementById("'+visualDiv+'")')
        varMetric   = js.var('metric', js.s(self.metric))
        varGroup    = js.var('dimension', js.s(self.group))
        zdSDK = self.__connectionPromise()
        #. Jquery onchange handlers for the filters
        metricJsParams = {'s':'metric'}
        metricJsParams.update(self.metricParams)
        dimensionJsParams = {'s':'dimension'}
        dimensionJsParams.update(self.groupParams)
        metricJS = t.filterJS % metricJsParams
        dimensionJS = t.filterJS %  dimensionJsParams
        # wrap everything up as the require callback body
        cb = visLocation + varMetric + varGroup + zdSDK + metricJS + dimensionJS
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







        
