# -*- coding: utf-8 -*-
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
import json
import pandas as pd
from zoomdata.src.rest import RestCalls
from zoomdata.src.static_builder import Template, JSBuilder, StaticFiles
from zoomdata.src.datatypes import Attribute, Metric, Filter, TimeFilter
from random import randint
from IPython.display import display, HTML

rest    = RestCalls()
js      = JSBuilder()
templ   = Template()
static  = StaticFiles()

class Graph(object):

    def __repr__(self):
        return """To execute this please add brackets at the end of the expression () or append .execute()"""

    def __init__(self, source, init_data, chart, shortcut=True ):
        self.__source = source
        self.__data = init_data
        self.__lastRender = {}
        self.__chart = chart
        self.__shortcut = shortcut
        self.__groupby  = []
        self.__metric   = []
        self.__trend    = []
        self.__yaxis    = []  
        self.__xaxis    = []  
        self.__yaxis1   = []  
        self.__yaxis2   = []  
        self.__filters  = []
        self.__timeFilter = None
        self.__colors   = []
        self.__error    = False

        self.__showPickers = True
        self.__width = 800
        self.__height = 400
        self.__pickers = {}

        if not shortcut:
            self.chart(chart)
        
    def __clear_attrs__(self):
        self.__groupby  = []
        self.__metric   = []
        self.__trend    = []
        self.__yaxis    = []  
        self.__xaxis    = []  
        self.__yaxis1   = []  
        self.__yaxis2   = []  
        self.__filters  = []
        self.__colors   = []
        self.__timeFilter = None
        self.__error    = False
        self.__showPickers = True
        self.__width = 800
        self.__height = 400
        if not self.__shortcut:
            self.__chart = "Bars"
        self.__pickers = {}

    def __call__(self):
        return self.execute()

    def nopickers(self):
        self.__showPickers = False
        return self

    def width(self, width):
        self.__width = width
        return self

    def height(self, height):
        self.__height = height
        return self

    def groupby(self, *args):
        fields = []
        if isinstance(args[0], list):
            args = args[0]
        for f in args:
            if not isinstance(f, Attribute):
                print('All group by parameters must be Attribute objects')
                self.__error = True
                return self
            self.__groupby.append(f.getval())
        return self

    def filter(self, *args):
        filters = args
        if isinstance(args[0], list):
            filters = args[0]
        for f in filters:
            if not isinstance(f, Filter):
                print('Filter parameters must be a Filter object')
                self.__error = True
                return self
        self.__filters = [f.getval() for f in filters]
        return self

    def time(self, time):
        if not isinstance(time, TimeFilter):
            print("Time parameter should be TimeFilter object")
            self.__error = True
            return self
        self.__timeFilter = time.getval()
        return self

    def trend(self, timefield):
        if not isinstance(timefield, Attribute):
            print('Trend field should be an Attribute object')
            self.__error = True
        else:
            self.__trend = timefield.getval()
        return self

    def metric(self, metric):
        if not isinstance(metric, Metric):
            print('metric field should be an Metric object')
            self.__error = True
        else:
            self.__metric = metric.getval()
        return self

    def x(self, axis):
        if not isinstance(axis, Metric):
            print('X Axis field should be an Metric object')
            self.__error = True
        else:
            self.__xaxis = axis.getval()
        return self

    def y(self, axis):
        if not isinstance(axis, Metric):
            print('Y Axis field should be an Metric object')
            self.__error = True
        else:
            self.__yaxis = axis.getval()
        return self

    def y1(self, axis):
        if not isinstance(axis, Metric):
            print('Y1 Axis field should be an Metric object')
            self.__error = True
        else:
            self.__yaxis1 = axis.getval()
        return self

    def y2(self, axis):
        if not isinstance(axis, Metric):
            print('Y2 Axis field should be an Metric object')
            self.__error = True
        else:
            self.__yaxis2 = axis.getval()
        return self

    def colors(self, colors):
        self.__colors = colors
        return self

    def chart(self, chart):
        if chart not in self.__data['source_charts'] and not self.__shortcut: # If is an active visualization for the source
            self.__error = True
            print('Chart type not found or not configured. Supported charts for "%s" are:' % self.__data['source_name'])
            print('\n'.join(self.__data['source_charts']))
        if not self.__shortcut:
            self.__chart = chart
        return self

    def __validate_fields(self, pickers):
        fields = self.__source.fields()
        for key in pickers:
            if pickers[key]:
                if not isinstance(pickers[key], list):
                    pickers[key] = [pickers[key]]
                for field in pickers[key]:
                    row = fields.loc[fields['Name'] == field['name']]
                    if not row.empty:
                        flabel = row.iloc[0]['Label']
                        ftype  = row.iloc[0]['Type']
                        field.update({'label':flabel, 'type':ftype})
                        if ftype == "TIME" :
                            field['sort']['name'] = field['name']
                            if not field.get('func', False):
                                field.update({'func':'YEAR'})
                    else:
                        print("Field %s was not found in the source fields definition" % field['name'])
                        return False
        return pickers
    
    def __setJSCode(self, visualDiv):
        creds = {'key': self.__data['source_key']}
        histogram =  "true" if "Histogram" in self.__chart else "false"
        # Default pickers values to render the table
        defPickers = { "field": self.__groupby or False,
                      "metric": self.__metric or False,
                      "trend": self.__trend or False,
                      "y": self.__yaxis or False,
                      "x": self.__xaxis or False,
                      "y1": self.__yaxis1 or False,
                      "y2": self.__yaxis2 or False,
                }
        defPickers = self.__validate_fields(defPickers)
        if not defPickers:
            self.__clear_attrs__()
            return False
        initVars = [
            static.jstools(),
            js.var('v_defPicker', js.s(defPickers)),
            js.var('v_credentials', js.s(creds)),
            js.var('v_conf', js.s(self.__data['conf'])),
            js.var('v_source', js.s(self.__data['source_name'])),
            js.var('v_filters', js.s(self.__filters)),
            js.var('v_time', js.s(self.__timeFilter)),
            # js.var('v_vars', js.s(self.variables)),
            js.var('v_vars', js.s({})),
            js.var('v_colors', js.s(self.__colors)),
            js.var('v_divLocation','document.getElementById("'+visualDiv+'")'),
            js.var('v_chart', js.s(self.__chart)),
            js.var('v_showPickers', js.s(self.__showPickers)),
            js.var("v_isHistogram", histogram)
        ]
        initVars = "".join(initVars)
        code = static.jscode('chart')
        #Wrap it up!
        jscode = code.replace("_INITIAL_VARS_", initVars)
        return jscode

    def execute(self): 
        """Set up of the final code snippet to be rendered"""
        if self.__error:
            self.__clear_attrs__()
            return False
        renderCount = randint(0, 10000)
        w, h = self.__width, self.__height
        visualDiv = 'visual%s' % (str(renderCount))
        self.__showPickers = False if self.__chart in ['Map: Markers'] else self.__showPickers
        jscode = self.__setJSCode(visualDiv)
        if jscode:
            styles = templ.styleTags % (static.css())
            htmlcode = templ.confirmcss + templ.bootstrapcss + styles \
                        + templ.divFilters + templ.loadmsg + templ.divChart % (visualDiv, str(w), str(h))
            jscode = templ.scriptTags % (jscode)
            # This is for debugging 
            self.__clear_attrs__()
            self.__lastRender = {'html': htmlcode, 'js': jscode}
            iframe = templ.iframe % (templ.requirejs, htmlcode + jscode, str(w+40), str(h+90) )
            return HTML(iframe)
        return False

    def _getRawHtml(self):
        try:
            import jsbeautifier
            from bs4 import BeautifulSoup as bs
            soup=bs(self.__lastRender['html'],"lxml")
            html=soup.prettify()
            jscode = jsbeautifier.beautify(self.__lastRender['js'])
            print (html+'\n'+jscode)
        except ImportError:
            print ('Modules jsbeautifier and beautifulsoup4 are required for this feature')


