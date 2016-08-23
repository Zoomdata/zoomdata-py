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
import os
import json

class Template(object):

    def __init__(self):
        # RequireJS CDN
        self.requirejs = '<script src="https://cdnjs.cloudflare.com/ajax/libs/require.js/2.2.0/require.min.js"></script>'
        self.confirmcss   ='<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/jquery-confirm/2.5.1/jquery-confirm.min.css" type="text/css" media="screen"/>'
        self.bootstrapcss = '<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css" type="text/css" media="screen"/>'
        self.styleTags = '<style type="text/css" media="screen">%s</style>'
        #Iframe where everything will be rendered
        self.iframe = """
                        <script type="text/javascript">var kernel = IPython.notebook.kernel</script>
                        <iframe 
                            srcdoc='<div align="center">%s %s</div>' 
                            src='' 
                            width='%s' 
                            height='%s' 
                            frameborder='0'>
                        </iframe> """ 

        self.loadmsg = '<p id="load-message" style="margin-top:10px" align="center">Loading visualization...</p>'

        # Output messages for getData
        self.logdata = "<div id='fetch%d'></div><div id='done%d'></div>"

        # Javascript tags to enclose all the js code
        self.scriptTags = '<script type="text/javascript">%s</script>' 

        # Div where the chart is rendered (by echartjs)
        self.divChart = '<div id="%s" class="zd medium" style="width:%spx; height:%spx; top:20%%"></div>'

        # Container div for the filters (metric, dimension) drop-downs
        self.divFilters = '<div id="pickers" style="display:inline-block;margin-top:5px" align="center"></div>' 



class JSBuilder(object):
    def __init__(self):
        pass
        
    def createFunc(self, funcName='', params=[], body='', anon=False, caller=''):
        """ Return a str representation of a js function. Params are:
                funcName(str):      The name of the function
                params(list/str):   The list of the paramters, it can be a list of strings or a single string
                body(str):          The body of the function
                anon(bool):         If is an anonymus function or not. If true, funcName won't be used
                caller(str):        Name of the obj that calls the function
        """
        if isinstance(params,(str)):
            params = [params]
        params = ','.join(params) if params else ''
        funcParams = (params,body) if anon else (funcName,params,body)
        funcFormat = 'function(%s){%s}' if anon else 'function %s(%s){%s}' 
        jsFunc = funcFormat % funcParams
        if caller:
            jsFunc = caller + '.' + jsFunc
        return jsFunc

    def consoleLog(self, msg='', type='log', obj=False):
        msg = "'%s'" % msg
        msg = '%s,%s' % (msg, obj) if obj else msg
        return 'console.%s(%s);' % (type, msg)

    def var(self, name,value):
        return 'var %s = %s;' % (name,value)

    def setVars(self, json, params=()):
        """Set javascript variables names as values 
        to a json object"""
        if isinstance(params,(str)):
            params = (params)
        json = json.replace('"%s"','%s')
        return json % params

    def s(self, expr):
        #A jsonify tool
        return json.dumps(expr)


class StaticFiles(object):
    def __init__(self):
        pass

    def js(self, fname):
        code = ''
        path = os.path.dirname(os.path.realpath(__file__))
        file = path+'/static/js/'+fname+'.js'
        with open(file) as f: # The embeding visualization code
            code = ''.join(f.readlines())
            # Remove the license 
            code = code.split('**/')[1]
        return code 

    def css(self):
        styles = ''
        path = os.path.dirname(os.path.realpath(__file__))
        with open(path+'/static/css/style.css') as f: #Set of functions used within the script
            styles = ''.join(f.readlines())
        return styles 

