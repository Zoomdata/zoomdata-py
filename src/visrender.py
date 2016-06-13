#/usr/bin/python3
import os
import urllib3
import json
import base64
from .jsbuilder import JSBuilder
from .templates import Template
from IPython.display import HTML

js = JSBuilder()
t = Template()

class VisRender(object):
    """VisRender will render the required HTML and JS code
        to render the visualization based on the specified chart type
    """
    def __init__(self, params):
        self.deps = ['ZoomdataSDK','jquery']
        self.conf =  params['conf']
        self.credentials = params['credentials'] 
        self.paths = params['paths'] 
        self.width = params['width']
        self.height = params['height']
        self.source = params['source']
        self.chart = params['chart']
        self.query = params['query']
        self.variables = params['variables']
        self.metric = params['metric']
        self.group = params['group']

    def createClient(self):
        credentials = {
                'credentials': {'key': self.credentials},
                'application': {'secure': self.conf['secure'], 
                                'host': self.conf['host'], 
                                'port': self.conf['port'], 
                                'path': self.conf['path']}
                }
        params = js.s(credentials)
        return 'ZoomdataSDK.createClient(%s)' % (params)

    def setRequireConf(self):
        #Set the require configuration part
        return 'require.config({paths:%s});' % js.s(self.paths)

    def getJSTools(self):
        tools = ''
        path = os.path.dirname(os.path.realpath(__file__))
        with open(path+'/js/tools.js') as t: #Set of functions used within the script
            tools = ''.join(t.readlines())
        return tools

    def connectionPromise(self):
        """Returns the string associated to the 
        promise that connects with ZD and creates the visualization"""
        prom = self.createClient()
        p ='window.client = client; return(client)'
        then = '.then(%s)' % (js.createFunc(params='client',body=p, anon=True))
        visualconf = {'element':'%s', 'config': self.query}
        visualconf.update( { 'source': {'name': self.source},
                             'visualization': self.chart,
                             'variables': '%s' #Initialization variables
                           })
        p = js.s(visualconf)
        #NOTE: variables goes first because setVars re-organizes the dict 
        p = js.setVars(p, ('variables','visLocation')) #set the element for echarts rendering

        # The function .done is where the Thread object is created
        # and the specific data such as groups, variables, parameters,
        # etc for the specific visualization being loaded
        done = '.done(%s);' % (js.createFunc(params='result',body=t.doneBody, anon=True))
        test = 'console.log("Requesting visualization...");'
        p = 'client.visualize(%s)%s' % (p, done)
        p = test + p
        then1 = '.then(%s);' % (js.createFunc(params='client',body=p, anon=True))
        return prom+then+then1

    def getPickerOptions(self):
        opt = t.optionFmt % ('','Select option')
        #Include the count/volume in the metrics
        count = t.optionFmt % ('count','Count')
        #Options for the metric operators picker
        oper  = t.optionFmt % ('min','Min')
        oper += t.optionFmt % ('max','Max')
        oper += t.optionFmt % ('sum','Sum')
        oper += t.optionFmt % ('avg','Avg')
        return opt, count, oper
    
    def setListBarTrend(self, renderCount):
        """Wraps and render all the JS code inside the require module"""
        # These vars hold the selected dataAccessor
        yAxis1 = js.var('metricAccessor', 'Y')
        yAxis2 = js.var('metricAccessor', 'Y')
        #HTML Pickers
        opt, count, oper = self.getPickerOptions()
        pickers = t.selectFmt % ('met-span','Y1 Axis', 'metric1', opt+count)
        pickers += t.selectFmt % ('met-span','Y2 Axis', 'metric2', opt+count)
        pickers += t.selectFmt % ('met-span','Time Attr', 'time', opt)
        # pickers += t.selectFmt % ('op-span','Op', 'func' , opt+oper)
        pickers = t.divFilters % (pickers)
        # ===Jquery onchange handlers for the pickers========
        pickersJS = t.metricPicker % {'metID':'metric1'}
        pickersJS += t.metricPicker % {'metID': 'metric2'}
        pickersJS += t.funcPicker 
        # wrap everything up as the require callback body
        cb = tools + visLocation + varVariables + varFilters + varChart + varMetric \
            + varGroup + varOperator + zdSDK + pickersJS
        reqCallback = js.createFunc(params=self.deps, body=cb, anon=True)
        req = 'require(%s,%s)' % (js.s(self.deps), reqCallback)
        return req, pickers

    def getPickers(self):
        opt = t.optionFmt % ('','Select option')
        #Options for the metric operators picker
        oper  = t.optionFmt % ('min','Min')
        oper += t.optionFmt % ('max','Max')
        oper += t.optionFmt % ('sum','Sum')
        oper += t.optionFmt % ('avg','Avg')
        #Include the count/volume in the metrics
        count = t.optionFmt % ('count','Count')
        pickers = ""
        if self.chart not in ["Line & Bars Trend"]:
            pickers = t.selectFmt % ('grp-span','Dimension', 'group', opt)
            pickers += t.selectFmt % ('met-span','Metric', 'metric1', opt+count)
        else:
            pickers = t.selectFmt % ('met-span','Y1 Axis', 'metric1', opt+count)
            pickers += t.selectFmt % ('met-span','Y2 Axis', 'metric2', opt+count)
        pickers += t.selectFmt % ('op-span','Operation', 'func' , opt+oper)
        return t.divFilters % (pickers)

    def wrapper(self, renderCount):
        """Wraps and render all the JS code inside the require module"""
        tools = self.getJSTools()
        visualDiv = 'visual%s' % (str(renderCount))
        varChart = js.var('chart',js.s(self.chart))
        visLocation = js.var('visLocation','document.getElementById("'+visualDiv+'")')
        varFilters  = js.var('filters', '[]')
        varVariables= js.var('variables', js.s(self.variables))
        # These vars hold the selected dataAccessor
        varMetricAccessor  = js.var('metricAccessor', '""')
        varGroupAccessor  = js.var('groupAccessor', '""')
        # These var hold the selected metric operator 
        varOperator = js.var('metricOp','""')
        #These two variables hold the selected metric and dimensions objects
        varMetric   = js.var('metric', js.s(self.metric))
        varGroup    = js.var('group', js.s(self.group))
        # The kernel variable to communicate python-js
        varKernel   = js.var('kernel', 'Ipython.notebook.kernel')
        #The promise with the SDK connection code
        zdSDK = self.connectionPromise()
        #. Jquery onchange handlers for the pickers
        pickersJS = ""
        if self.chart not in ["Line & Bars Trend"]:
            pickersJS = t.groupPicker 
            pickersJS += t.metricPicker % {'metID':'metric1'}
        else:
            pickersJS = t.metricPicker % {'metID':'metric1'}
            pickersJS += t.metricPicker % {'metID': 'metric2'}
        pickersJS += t.funcPicker 
        # wrap everything up as the require callback body
        cb = tools + visLocation + varVariables + varFilters + varChart + varMetric \
            + varGroup + varOperator + zdSDK + pickersJS
        reqCallback = js.createFunc(params=self.deps, body=cb, anon=True)
        return 'require(%s,%s)' % (js.s(self.deps), reqCallback)

    def getVisualization(self, renderCount):
        """Set up of the final code snippet to be rendered"""
        w, h = self.width, self.height
        visualDiv = 'visual%s' % (str(renderCount))
        pickers = ''
        if self.chart not in ['Map: Markers']:
            pickers = self.getPickers()
        # if self.chart == 'Line & Bars Trend':
            # req, pickers = self.setListBarTrend(renderCount)
        htmlcode = pickers + t.loadmsg + t.divChart % (visualDiv, str(w), str(h))
        jscode = t.scriptTags % (self.setRequireConf(), self.wrapper(renderCount))
        html = htmlcode + jscode
        iframe = t.iframe % (t.requirejs, html, str(w+40), str(h+80) )
        return iframe, htmlcode, jscode
