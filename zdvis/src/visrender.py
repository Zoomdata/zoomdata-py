#/usr/bin/python3
import os
import json
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
        self.token = params['token'] 
        self.paths = params['paths'] 
        self.width = params['width']
        self.height = params['height']
        self.source = params['source']
        self.chart = params['chart']
        self.query = params['query']
        self.variables = params['variables']
        self.filters= params['filters']
        self.time = params['time']
        self.colors = params['colors']
        #if graph_filters are specified, overwrite the ZD._filters
        #This implementation is is for the following filter syntax:
        # Ex: {'field1':['value1','value2'], 'field2':'value1'}
        filterdict= params['graph_filters']
        if filterdict:
            self.filters = []
            for field in filterdict:
                filt = {'operation':'IN'}
                filt.update({'path': field})
                if isinstance(filterdict[field], (str, int, bool)):
                    filterdict[field] = [filterdict[field]]
                filt.update({'value':filterdict[field]})
                self.filters.append(filt)

    def getJSTools(self):
        tools = ''
        path = os.path.dirname(os.path.realpath(__file__))
        with open(path+'/static/js/tools.js') as tool: #Set of functions used within the script
            tools = ''.join(tool.readlines())
        return tools

    def getCss(self):
        styles = ''
        path = os.path.dirname(os.path.realpath(__file__))
        with open(path+'/static/css/style.css') as f: #Set of functions used within the script
            styles = ''.join(f.readlines())
        return styles 

    def getJSCode(self, chart):
        code = ''
        path = os.path.dirname(os.path.realpath(__file__))
        file = path+'/static/js/render/'+chart+'.js'
        with open(file) as f: #Set of functions used within the script
            code = ''.join(f.readlines())
        return code 

    def getInitVars(self, defPicker, renderCount):
        #=== Common Vars declaration =======
        tools = self.getJSTools()
        defPicker = js.var('v_defPicker', js.s(defPicker))
        creds = {'key': self.credentials}
        cred = js.var('v_credentials', js.s(creds))
        conf = js.var('v_conf', js.s(self.conf))
        source = js.var('v_source', js.s(self.source))
        filters = js.var('v_filters', js.s(self.filters))
        timeFilter = js.var('v_time', js.s(self.time))
        variables = js.var('v_vars', js.s(self.variables))
        colors = js.var('v_colors', js.s(self.colors))
        visualDiv = 'visual%s' % (str(renderCount))
        divLocation = js.var('v_divLocation','document.getElementById("'+visualDiv+'")')
        return tools + cred + conf + source + filters + timeFilter + variables + colors + divLocation + defPicker
    
    def setJSCode(self, renderCount, pickers, showPickers):
        # Default pickers values to render the table
        defPicker = False
        if pickers: 
            defPicker = { "field":pickers.get('attribute',False),
                          "metric":pickers.get('metric',False),
                          "func":pickers.get('operation',False),
                          "y":pickers.get('yaxis',False),
                          "yop":pickers.get('y-operation',False),
                          "x":pickers.get('xaxis',False),
                          "xop":pickers.get('x-operation',False),
                          "y1":pickers.get('y1',False),
                          "y2":pickers.get('y2',False),
                          "y1op":pickers.get('op1',False),
                          "y2op":pickers.get('op2',False),
                          "trend":pickers.get('trend',False),
                          "time":pickers.get('unit',False),
                          "limit":pickers.get('limit',False)
                    }
        # Vars declaration 
        initVars = self.getInitVars(defPicker, renderCount)
        code = self.getJSCode('chart')
        chart = js.var('v_chart', js.s(self.chart))
        showP = js.var('v_showPickers', js.s(showPickers))
        #Wrap it up!
        _initial_vars = initVars + chart + showP
        jscode = code.replace("_INITIAL_VARS_", _initial_vars)
        return jscode

    def getVisualization(self, renderCount, pickers, showPickers):
        """Set up of the final code snippet to be rendered"""
        w, h = self.width, self.height
        visualDiv = 'visual%s' % (str(renderCount))
        showPickers = False if self.chart in ['Map: Markers'] else showPickers
        jscode = self.setJSCode(renderCount, pickers, showPickers)
        styles = t.styleTags % (self.getCss())
        htmlcode = t.confirmcss + t.bootstrapcss + styles + t.divFilters + t.loadmsg + t.divChart % (visualDiv, str(w), str(h))
        jscode = t.scriptTags % (jscode)
        html = htmlcode + jscode
        iframe = t.iframe % (t.requirejs, html, str(w+40), str(h+90) )
        return iframe, htmlcode, jscode
