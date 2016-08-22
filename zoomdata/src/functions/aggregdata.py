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
from zoomdata.src.datatypes import Attribute, Metric, Filter, TimeFilter

rest = RestCalls()

class AggregatedData(object):
    """
    """

    def __repr__(self):
        return """To execute this please add brackets at the end of the expression () or append .execute()"""

    def __init__(self, init_data, limit=10000):
        self.__data = init_data
        self.__dimensions = []
        self.__metrics  = []
        self.__filters  = []
        self.__time     = None
        self.__error    = False

    def __clear_attrs__(self):
        self.__dimensions = []
        self.__metrics  = []
        self.__filters  = []
        self.__time     = None
        self.__error    = False

    def __call__(self):
        return self.execute()

    def groupby(self, *args):
        if not args: return self
        attrs = args
        aggregations = []
        aggregationWindows = []
        if isinstance(args[0], list):
            attrs = args[0]
        for f in attrs:
            if not isinstance(f, Attribute):
                print('All grouby parameters must be Attribute objects')
                self.__error = True
                return self
            f = f.getval()
            a = {'field':{ 'name':f['name'] }, 'type': 'TERMS' }
            #Model: { "field": { "name": "field" }, "type": "TERMS" }, or
            #Model: { "field": { "name": "timefield" }, "type": "TIME", "granularity": "YEAR" },
            if f['type'] == 'TIME':
                a.update({'type':'TIME', 'granularity':f['granularity']})
            aggregations.append(a)

            agw = {"limit": f['limit'], 
                  "sort": {
                          "direction": f['sort']['dir'],
                          "metric": {}, 
                          "type": "METRIC"
                      }
                  }
            #Model: { "limit": 50, "sort": { "direction": "DESC", "metric": { "type": "COUNT" }, "type": "METRIC" } },
            if f['sort']['name'] == "count":
                agw['sort']['metric'].update({'type':'COUNT'})
            #Model: { "limit": 20, "sort": { "direction": "ASC", "type": "ALPHABETICAL" } }
            elif f['sort']['name'] == f['name']:
                agw['sort']['type'] = 'ALPHABETICAL'
                if agw.get('metric', False):
                    agw.pop('metric')
            #Model:{ "limit": 20, "sort": { "direction": "ASC", "metric": { "field": {"name": "qtysold"}, "function": "SUM", "type": "FIELD" }, "type": "METRIC" } }
            else:
                agw['sort']['metric'].update({'field':{'name':f['sort']['name']},
                                              'type':'FIELD', 
                                              'function':f['sort']['func']})
            aggregationWindows.append(agw)
        #TODO: Support type simple and Histogram
        self.__dimensions = [{
                        'aggregations': aggregations, 
                        'window':{ 'aggregationWindows': aggregationWindows, 
                                    'type': 'COMPOSITE'}
                    }]
        return self

    def metrics(self, *args):
        if not args: return self
        mets = []
        if isinstance(args[0], list):
            args = args[0]
        for m in args:
            if not isinstance(m, Metric):
                print('All metrics parameters must be Metric objects')
                self.__error = True
                return self
            #Model: { "type": "COUNT" }
            m = m.getval()
            if m['name'] == 'count':
                self.__metrics.append({'type': 'COUNT'})
            #Model: { "field": { "name": "commission" }, "function": "SUM", "type": "FIELD" }
            else:
                self.__metrics.append({
                        'field': {'name': m['name']},
                        'function': m['func'],
                        'type': 'FIELD'
                    })
            #TODO: Add support to percentile metrics
        return self

    def filter(self, *args):
        if not args: return self
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
        if not time: return self
        if not isinstance(time, TimeFilter):
            print("Time parameter should be TimeFilter object")
            self.__error = True
            return self
        self.__time = time.getval()
        return self

    def execute(self):
        if self.__error:
            self.__clear_attrs__()
            return False
        if not self.__dimensions:
            print('Fields to group by (dimensions) are required for this function. Add .groupby(Field1, Field2)')
            self.__clear_attrs__()
            return False
        server_url = self.__data['url']
        headers = self.__data['headers']
        source_id = self.__data['source_id']
        source_key = self.__data['source_key']

        try:
            import ssl
            from websocket import create_connection

            socketUrl = server_url + "/websocket?key=" + source_key
            socketUrl = socketUrl.replace('https','wss')
            request = {
                         "api": "VIS",
                         "cid": "f3020fa6e9339ee5829f6e2caa8d2e40",
                         "type": "START_VIS",
                         "sourceId": source_id,
                         "aggregate": True,
                         "dimensions": self.__dimensions,
                         "metrics": self.__metrics,
                         "filters": self.__filters,
                         "time": self.__time,
            }
            # WS request
            ws = create_connection(socketUrl)
            ws.send(json.dumps(request))
            req_done = False
            dataframe = []
            maxloop = 0
            while maxloop <= 30:
                frame = ws.recv() #NOTE: This will hang if no data is received
                if 'NOT_DIRTY_DATA' in frame:
                    ws.close()
                    break
                if 'INTERNAL_ERROR' in frame:
                    ws.close()
                    print('An error occured:')
                    frame = json.loads(frame)
                    if frame.get('details',False):
                        print(frame['details'])
                    else: 
                        print(frame)
                    return False
                maxloop += 1
                frame = frame.replace('false','False')
                frame = frame.replace('null','None')
                frame = eval(frame)
                dataframe.extend(frame.get('data',[]))

            #Parsing takes a little more due to they're different for each visuals
            if maxloop == 30: # There was an error
                ws.close()

            if dataframe:
                #Parse the right field type
                dfParsed = []
                columns = []
                fields = []
                for f in self.__dimensions[0]['aggregations']:
                    if f['field'].get('form',False):
                        fields.append(f['field']['form']) #Fusion sources should be based on the form attr
                    else:
                        fields.append(f['field']['name'])
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
                dataframe = pd.DataFrame(dataframe, columns=fields)
                vis = rest.getSourceById(server_url, headers, source_id)
                for f in vis['objectFields']:
                    if f['name'] in fields and f['type'] == 'TIME': 
                        dataframe[f['name']] = pd.to_datetime(dataframe[f['name']])
                #Clean all attributes
                self.__clear_attrs__()
                return dataframe
            print('No data was returned')
            return False

        except ImportError:
            print ('No websocket module found. Install: pip3 install websocket-client')
