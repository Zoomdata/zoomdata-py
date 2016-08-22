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
import pandas as pd
from .functions.rawdata import RawData
from .functions.aggregdata import AggregatedData
from .functions.graph import Graph
from zoomdata.src.rest import RestCalls
rest = RestCalls()

class Source(object):

    def __init__(self, data):
        #Attrs
        self.id     = data['source_id']
        self.name   = data['source_name']
        self.__data = data

        #Methods
        self.graph      = Graph(self, data,'Bars', shortcut=False)
        self.bars       = Graph(self, data,'Bars')
        self.donut      = Graph(self, data,'Donut')
        self.pie        = Graph(self, data,'Pie')
        self.kpi        = Graph(self, data,'KPI')
        self.treemap    = Graph(self, data,'Tree Map')
        self.heatmap    = Graph(self, data,'Heat Map')
        self.rawdata    = RawData(data)
        self.first      = RawData(data, limit=1)
        self.data       = AggregatedData(data)
        # self.setvisualization = Visualization()


    def fields(self, conf={}):
        """
        Retrieve or modify the fields from the source. It one optional parameters:
            - conf: Dictionary: The new configuration for the fields using field name as key. Ex:
                    {'field_name1':{'type':'new_type','visible':True, 'label':'New Label'}, {'field_name2':...}}}
                    If no conf is specified, the current fields conf will be retrieved.
        """
        server_url = self.__data['url']
        headers = self.__data['headers']
        vis = rest.getSourceById(server_url, headers, self.id)
        if vis and not conf: # Only print the attrs config. No update
            print('')
            dataframe = []
            for f in vis['objectFields']:
                dataframe.append([f['name'], f['label'], f['type'], f['visible']])
            dataframe = pd.DataFrame(dataframe, columns=['Name','Label','Type','Visible'])
            return dataframe
        elif vis and conf: #Do not print, just update
            fields = [f for f in conf.keys()]
            for f in vis['objectFields']:
                if f['name'] in conf:
                    for key in conf[f['name']].keys():
                        if key in f: # Check if the key is in the original, to avoid inserting wrong keys
                            f[key] = conf[f['name']][key]
            print('Updating source fields...')
            if(rest.updateSourceDefinition(server_url, headers, self.id, vis)):
                print('Done!')
