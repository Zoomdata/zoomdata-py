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
from zoomdata.src.visdefinition import VisDefinition
from zoomdata.src.rest import RestCalls

rest = RestCalls()
vd = VisDefinition()

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
        self.table      = AggregatedData(data, simple=True)
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
        if not vis:
            return False
        if vis and not conf: # Only print the attrs config. No update
            print('')
            dataframe = []
            # Fields
            for f in vis['objectFields']:
                dataframe.append([f['name'], f['label'], f['type'], f['visible'],'-'])
            # Formulas
            formulas = vis.get('formulas',[])
            for f in formulas:
                dataframe.append([f['name'], f['label'], 'CALC', f['valid'], f['script']])
            dataframe = pd.DataFrame(dataframe, columns=['Name','Label','Type','Visible','Script'])
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

    def connection(self):
        """
        Return the connection parameters for a the source. 
        """
        print('Fetching source parameters...')
        server_url = self.__data['url']
        headers = self.__data['headers']
        vis = rest.getSourceById(server_url, headers, self.id)
        if vis:
            print('')
            print('Name : '+vis['name'])
            print('ID : '+self.id)
            print('Storage: '+vis['type'])
            for key in vis['storageConfiguration']:
                print(key+': '+str(vis['storageConfiguration'][key]))

    def setVisualization(self, name, definition={}):
        """
        Configure a visualization to the source. The specified visualization must be supported by Zoomdata
        and by the source. Ex: You can not specify a Map if the source does not have maps information (lat/long)
        """
        server_url = self.__data['url']
        headers = self.__data['headers']
        if(headers['Authorization']):
            # 1. First get the ID of the specific visualization
            print('Checking allowed chart types...')
            if not (self.__data['source_charts']):
                allVisuals = rest.getVisualizationsList(server_url, headers)
            visualsNames = [v['name'] for v in allVisuals]
            if name not in visualsNames:
                print('Visualization type not found or not configured. Supported visualizations are:')
                print('\n'.join(visualsNames))
            else:
                visId = [v['id'] for v in allVisuals if v['name'] == name]
                result = False
                if name == 'Map: Markers':
                    result = vd.setMapMarkers(visId[0], definition, server_url, headers, self.id)
                elif name == 'Line & Bars Trend':
                    result = vd.setLineBarsTrend(visId[0], definition, server_url, headers, self.id)
                if result:
                    self.__data['source_charts'].append(name)
                else:
                    print('Error: Probably the add/update feature is not supported yet for this chart type.')
        else:
            print('You need to authenticate: ZD.auth("user","password")')

    def append(self, dataframe): 
        """Updates the source by appending the new data to the existing one.
           Parameters:
                dataframe: Contains the data used to populate the source, commonly a pandas dataframe is used
        """
        server_url = self.__data['url']
        headers = self.__data['headers']
        sources = rest.getAllSources(server_url, headers)
        # Validate if the source was deleted after closing/re-opening the notebook
        if self.name not in sources:  
            print('This is not a valid source anymore. Execute ZD.sources() to get a list of available sources')
        else:
            # Check if is a different source (deleted/created) with the same name
            source_id = rest.getSourceID(server_url, headers, self.name)
            if source_id != self.id:
                print('This is not a valid source anymore. Execute ZD.sources() to get a list of available sources')
            else:
                urlParams = { 'separator':',',
                              'contentType':'text/csv',
                              'includesHeader':'true',
                              'includesNewFields':'true' }
                #Convert dataframe from whatever it is to csv
                print('Parsing data...')
                try:
                    df = dataframe.to_csv() 
                    #If not corrected, pandas adds a column with a row counter. This column must not be part of the source data
                    if df[0] == ',':
                        rows = df.split('\n')
                        rows = [r.split(',',1)[-1] for r in rows]
                        df = '\n'.join(rows)
                except:
                    print('Invalid dataframe')
                resp, upd = rest.createSourceFromData(server_url, headers, \
                                                self.__data['account'], self.name, df, urlParams, False)
