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


