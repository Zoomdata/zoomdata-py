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

    def setRequireConf(self):
        #Set the require configuration part
        return 'require.config({paths:%s});' % js.s(self.paths)

    def getJSTools(self):
        tools = ''
        path = os.path.dirname(os.path.realpath(__file__))
        with open(path+'/js/tools.js') as t: #Set of functions used within the script
            tools = ''.join(t.readlines())
        return tools

    def getJSCode(self, chart):
        code = ''
        path = os.path.dirname(os.path.realpath(__file__))
        file = path+'/js/render/'+chart+'.js'
        with open(file) as f: #Set of functions used within the script
            code = ''.join(f.readlines())
        return code 

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

    def getInitVars(self, defPicker, renderCount):
        #=== Common Vars declaration =======
        tools = self.getJSTools()
        defPicker = js.var('v_defPicker', js.s(defPicker))
        cred = js.var('v_credentials', js.s(self.credentials))
        conf = js.var('v_conf', js.s(self.conf))
        source = js.var('v_source', js.s(self.source))
        filters = js.var('v_filters', '[]')
        variables = js.var('v_vars', js.s(self.variables))
        visualDiv = 'visual%s' % (str(renderCount))
        divLocation = js.var('v_divLocation','document.getElementById("'+visualDiv+'")')
        return tools + cred + conf + source + filters + variables + divLocation + defPicker
    
    def setCommonChart(self, renderCount, pickers):
        # Default values to render the table
        defPicker = { "dimension":pickers.get('attribute',''),
                      "metric":pickers.get('metric',''),
                      "limit":pickers.get('limit',40),
                      "operation":pickers.get('operation','')
                }
        # Vars declaration 
        initVars = self.getInitVars(defPicker, renderCount)
        code = self.getJSCode('common_charts')
        chart = js.var('v_chart', js.s(self.chart))
        # These vars hold the selected dataAccessor
        mAcc = js.var('v_metricAccessor', '""')
        gAcc = js.var('v_groupAccessor', '""')
        # These var hold the selected metric operator 
        varOp = js.var('v_metricOp','""')
        #These two variables hold the selected metric and dimensions objects
        met = js.var('v_metric', '{}')
        group = js.var('v_group', '{}')
        #Wrap it up!
        _initial_vars = initVars + chart + met + group + mAcc + gAcc + varOp 
        jscode = code.replace("_INITIAL_VARS_", _initial_vars)
        #The Pickers
        opt, count, oper = self.getPickerOptions()
        p1 = ""
        if 'kpi' not in  self.chart.lower():
            p1 = t.selectFmt % ('grp-span','Attribute', 'group', opt)
        p2 = t.selectFmt % ('met-span','Metric', 'metric', opt+count)
        p3 = t.selectFmt % ('op-span','Operation', 'func' , opt+oper)
        return jscode, t.divFilters % (p1+p2+p3)

    def setLineBarsTrend(self, renderCount, pickers):
        defPicker = { "yaxis1":pickers.get('y1',''),
                      "yaxis2":pickers.get('y2',''),
                      "operation1":pickers.get('op1',''),
                      "operation2":pickers.get('op2',''),
                      "trend":pickers.get('trend',''),
                      "unit":pickers.get('unit',''),
                      "limit":pickers.get('limit',1000)
                }
        code = self.getJSCode('line_bars_trend')
        initVars = self.getInitVars(defPicker, renderCount)
        trendGrp = js.var('v_trend', '{}')
        _initial_vars = initVars + trendGrp
        jscode = code.replace("_INITIAL_VARS_", _initial_vars)
        #The Pickers
        opt, count, oper = self.getPickerOptions()
        pickers = t.selectFmt % ('met-span','Y1 Axis', 'yaxis1', opt+count)
        pickers += t.selectFmt % ('op-span1','Operation1', 'func1' , opt+oper)
        pickers += t.selectFmt % ('met-span','Y2 Axis', 'yaxis2', opt+count)
        pickers += t.selectFmt % ('op-span2','Operation2', 'func2' , opt+oper)
        axisPickers = t.divFilters % pickers
        pickers = t.selectFmt % ('met-span','Trend Attr', 'trend-attr', opt)
        pickers += t.selectFmt % ('met-span','', 'time-unit', opt)
        timePickers = t.divFilters % pickers
        return jscode, axisPickers + timePickers

    def setLineTrendAttrs(self, renderCount, pickers):
        defPicker = { "metric":pickers.get('metric',''),
                      "group":pickers.get('attribute',''),
                      "trend":pickers.get('trend',''),
                      "operation":pickers.get('operation',''),
                      "unit":pickers.get('unit','none'),
                      "limit":pickers.get('limit',1000)
                }
        code = self.getJSCode('line_trend_attrs')
        initVars = self.getInitVars(defPicker, renderCount)
        trendGrp = js.var('v_trend', '{}')
        group = js.var('v_group', '{}')
        metric = js.var('v_metric', '{}')
        _initial_vars = initVars + trendGrp + group + metric
        jscode = code.replace("_INITIAL_VARS_", _initial_vars)
        #The Pickers
        opt, count, oper = self.getPickerOptions()
        pickers = t.selectFmt % ('dim-span','Attribute', 'group', opt)
        pickers += t.selectFmt % ('met-span','Y Axis', 'metric', opt+count)
        pickers += t.selectFmt % ('op-span','Operation', 'func' , opt+oper)
        mainPickers = t.divFilters % pickers
        pickers = t.selectFmt % ('time-span','Trend Attr', 'trend-attr', opt)
        pickers += t.selectFmt % ('unit-span','', 'time-unit', opt)
        timePickers = t.divFilters % pickers
        return jscode, mainPickers + timePickers

    def getVisualization(self, renderCount, pickers):
        """Set up of the final code snippet to be rendered"""
        w, h = self.width, self.height
        visualDiv = 'visual%s' % (str(renderCount))
        if self.chart in ['Map: Markers']:
            jscode, pickersDiv = self.setCommonChart(renderCount, pickers)
            pickersDiv  = ""
        elif self.chart in ['Line & Bars Trend']:
            jscode, pickersDiv = self.setLineBarsTrend(renderCount, pickers)
        elif self.chart in ['Line Trend: Attribute Values']:
            jscode, pickersDiv = self.setLineTrendAttrs(renderCount, pickers)
        else:
            jscode, pickersDiv = self.setCommonChart(renderCount, pickers)

        htmlcode = pickersDiv + t.loadmsg + t.divChart % (visualDiv, str(w), str(h))
        jscode = t.scriptTags % (self.setRequireConf(), jscode)
        html = htmlcode + jscode
        iframe = t.iframe % (t.requirejs, html, str(w+40), str(h+90) )
        return iframe, htmlcode, jscode
