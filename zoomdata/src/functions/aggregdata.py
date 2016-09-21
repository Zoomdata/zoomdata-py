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

    def __init__(self, init_data, simple=False):
        self.__data = init_data
        self.__is_simple = simple
        self.__dimensions = []
        self.__rawdimensions = []
        self.__rawmetrics = []
        self.__metrics  = []
        self.__sortby  =  False
        self.__sortdir  = 'DESC'
        self.__filters  = []
        self.__time     = None
        self.__error    = False
        self.__print_ws_requests = False
        self.__limit = 100000

    def __clear_attrs__(self):
        self.__dimensions = []
        self.__metrics  = []
        self.__filters  = []
        self.__sortby  =  False
        self.__time     = None
        self.__error    = False
        self.__rawdimensions = []
        self.__rawmetrics = []
        self.__print_ws_requests = False

    def __call__(self):
        return self.execute()

    def _wsrequest(self):
        """
        This option allows to print the ws url and request for debugging purpouses       
        """
        self.__print_ws_requests = True
        return self

    def groupby(self, *args):
        """
        Docstring for group by
        """
        if not args: return self
        attrs = args
        aggregations = []
        # Visualization data (COMPOSITE)
        aggregationWindows = []
        # Aggregated data (SIMPLE)
        aggregationSorts = []
        if isinstance(args[0], list):
            attrs = args[0]
        self.__rawdimensions = attrs
        for f in attrs:
            if not isinstance(f, Attribute):
                print('All grouby parameters must be Attribute objects')
                self.__error = True
                return self
            f = f.getval()
            a = {'field':{ 'name':f['name'] }, 'type': 'TERMS' }
            # Model: { "field": { "name": "field" }, "type": "TERMS" }, or
            # Model: { "field": { "name": "timefield" }, "type": "TIME", "granularity": "YEAR" }, or
            # Model: { "field"":{ "name": "qtysold" }, "type": "HISTOGRAM", histogramType: "AUTO" }
            # Time
            if f['type'] == 'TIME':
                a.update({'type': f['type'], 'granularity':f['granularity']})
            # Histogram
            if f['type'] == 'HISTOGRAM':
                a.update({'type':f['type'], 'histogramType':f['func']})
                func = f['func'].lower()
                value = f.get(func, False)
                if value:
                    a[func] = value
            aggregations.append(a)

            if not self.__is_simple: # COMPOSITE
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
                    agw['sort'].pop('metric')
                #Model:{ "limit": 20, "sort": { "direction": "ASC", "metric": { "field": {"name": "qtysold"}, "function": "SUM", "type": "FIELD" }, "type": "METRIC" } }
                else:
                    agw['sort']['metric'].update({'field':{'name':f['sort']['name']},
                                                  'type':'FIELD', 
                                                  'function':f['sort']['func']})
                aggregationWindows.append(agw)
            else: # SIMPLE data
                aggregationSorts.append({
                       "aggregation": a,
                       "direction": f['sort']['dir'],
                    })
        if not self.__is_simple:
            self.__dimensions = [{
                            'aggregations': aggregations, 
                            'window':{ 'aggregationWindows': aggregationWindows, 
                                        'type': 'COMPOSITE'}
                        }]
        else:
            self.__dimensions = [{
                            'aggregations': aggregations, 
                            'window':{ 'offset': 0, 
                                       'limit': 10**9,
                                       'sort': {
                                                'aggregationSorts':aggregationSorts, 
                                                'type':'ALPHABETICAL' },
                                       'type': 'SIMPLE'}
                            },{'aggregations':[]}]
        return self

    def metrics(self, *args):
        """
        Docstring for metrics
        """
        if not args: return self
        mets = []
        if isinstance(args[0], list):
            args = args[0]
        self.__rawmetrics = args
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
            elif "CALC" in m['func']:
                self.__metrics.append({
                        'formulaName': m['name'],
                        'type': 'CALCULATION'
                    })
            else:
                self.__metrics.append({
                        'field': {'name': m['name']},
                        'function': m['func'],
                        'type': 'FIELD'
                    })
            #TODO: Add support to percentile metrics
        return self

    def filter(self, *args):
        """
        Docstring for filters
        """
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

    def limit(self, limit):
        if not isinstance(limit, int):
            print('Incorrect value for the limit')
            self.__error = True
            return self
        self.__limit = limit
        return self

    def sortby(self, metric, direc="DESC"):
        if not isinstance(metric, Metric):
            print('The sortby paramenter must be a Metric object')
            self.__error = True
            return self
        if direc.upper() not in ['ASC','DESC']:
            print('Direction parameter for . sortby option is incorrect. Use "ASC" or "DESC"')
            self.__error = True
            return self
        self.__sortby = metric
        self.__sortdir = direc
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
        if self.__is_simple:
            for f in self.__rawdimensions:
                if f._Attribute__userlimit:
                    msg = "Individual limits for attributes are not allowed for table.\nUse the .limit() option instead for the table and remove the indivual limits"
                    print(msg)
                    self.__clear_attrs__()
                    return False
        server_url = self.__data['url']
        headers = self.__data['headers']
        source_id = self.__data['source_id']
        source_key = self.__data['source_key']

        # Only valid for SIMPLE and allows to sort by one of the selected metric
        if self.__sortby and self.__is_simple: 
            sortm = self.__sortby.getval()
            match = False
            for m in self.__rawmetrics:
                m = m.getval()
                if sortm['name'] == m['name'] and sortm['func'] == m['func']:
                    match = True
                    break
            if not match:
                print('The sorting metric must match (name and operation) one of the specified in the .metrics() option')
                self.__clear_attrs__()
                return False
            metric = {}
            if sortm['name'] == 'count':
                metric = {'type': 'COUNT'}
            elif "CALC" in sortm['func']:
                metric ={ 'formulaName': sortm['name'], 'type': 'CALCULATION' }
            else:
                metric = { 'field': {'name': sortm['name']}, 'function': sortm['func'], 'type': 'FIELD' }
            sort = {
                    'type': 'METRIC',
                    'metric': metric,
                    'direction': self.__sortdir,
                    'groups': []
                    }
            self.__dimensions[0]['window']['sort'] = sort

        try:
            import ssl
            from websocket import create_connection

            socketUrl = server_url + "/websocket?key=" + source_key
            socketUrl = socketUrl.replace('https','wss')
            start_vis = {
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

            request_data = {
                        "type":"REQUEST_DATA",
                        "cid":"f3020fa6e9339ee5829f6e2caa8d2e40",
                        "request":{
                                "caller":"RDP",
                                "delay":2005,
                                "columnsOffset":0,
                                "columnsCount":10**9,
                                "records": 10**18
                            }
                    }
            # WS request
            ws = create_connection(socketUrl)
            if self.__print_ws_requests:
                print(socketUrl)
                print('====================')
                print('      START_VIS     ')
                print('====================')
                print(json.dumps(start_vis))
                if self.__is_simple:
                    print('====================')
                    print('     REQUEST_DATA   ')
                    print('====================')
                    print(json.dumps(request_data))
            ws.send(json.dumps(start_vis))
            ndd = False
            dataframe = []
            maxloop = 0
            for x in range(30):
                frame = ws.recv() #NOTE: This will hang if no data is received
                if 'NOT_DIRTY_DATA' in frame:
                    if not self.__is_simple:
                        ws.close()
                        break
                    else:
                        ndd = True
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
                frame = json.loads(frame)
                dataframe.extend(frame.get('data',[]))
            else:
                ws.close()
            
            # Perform the second request for SIMPLE data
            if ndd and self.__is_simple:
                ws.send(json.dumps(request_data))
                for x in range(30):
                    frame = ws.recv()
                    if 'data' in frame:
                        frame = json.loads(frame)
                        dataframe.extend(frame.get('data',[]))
                    if 'REQUEST_DATA_DONE':
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
                else:
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
                opKeys = ['sum','avg','max','min','calc']
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
                    if not row[0] or isinstance(row[0], int) or not 'columnTotal' in row[0]:
                        dfParsed.append(row)
                dataframe = dfParsed
                dataframe = pd.DataFrame(dataframe, columns=fields)
                vis = rest.getSourceById(server_url, headers, source_id)
                for f in vis['objectFields']:
                    if f['name'] in fields and f['type'] == 'TIME': 
                        try:
                            dataframe[f['name']] = pd.to_datetime(dataframe[f['name']])
                        except:
                            pass
                #Clean all attributes
                self.__clear_attrs__()
                return dataframe
            print('No data was returned')
            return False

        except ImportError:
            print ('No websocket module found. Install: pip3 install websocket-client')
