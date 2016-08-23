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
import base64
import pickle
import pandas as pd
from time import sleep
from .rest import RestCalls
from .source import Source
from .visdefinition import VisDefinition
from .visrender import VisRender
from .config import *
from .static_builder import JSBuilder
from IPython.display import display, HTML

home_dir = os.path.expanduser('~')

SOURCES_JSON_FILE = home_dir + "/.sources.json"
USERDATA_FILE = home_dir + "/.userdata.pkl"

rest = RestCalls()
vd = VisDefinition()
js = JSBuilder()

def data(resp):
    return resp.data.decode('ascii')

class Zoomdata(object):

    """ Works as an API connector with Zoomdata services and SDK
    allowing to bring visualizations, work with sources, fetch and send data..
    """

    def __init__(self):
        """ To ensure maximum flexibility for the visualization configuration
        here must be setted all values that may change """

        #Main configurations
        self._conf = config
        protocol = 'https' if config['secure'] else 'http'
        self._serverURL = '%s://%s:%s%s' % (protocol, config['host'], config['port'], config['path'])
        self._source_credentials = {}

        if os.path.exists(SOURCES_JSON_FILE):
            with open(SOURCES_JSON_FILE,'r') as sc:
                self._source_credentials = json.load(sc)
        else: #Create it and leave it there
            with open(SOURCES_JSON_FILE, 'w') as sc:
                json.dump(self._source_credentials, sc)
            #Change the mode so anyone can use read/write it
            # os.chmod(SOURCES_JSON_FILE,0o666)

        # User authentication
        self._user = ''
        self._account = ''
        self._token = ''

        # Dataframe fetching attrs
        self._dframe= ''
        self._logcount = 0

        # Iframe size for the visualization
        self._width = 800
        self._height = 400

        # Visualization attrs
        self._source = ''
        self._chart = 'Bars' # A common default visualization
        self._renderCount = 0 # To render a different chart each time. (jquery element)
        self._credentials = ''  # This is the key to get the source key to get the visualization
        self._source_id = '' # This is the source id to get the source definition
        self._source_charts = [] # Active visualizations for the current source
        self._allowed_visuals = [] # All the visualizations names allowed by zoomdata
        self._variables = {} # This is a default configuration used to render a visualization. Usually extracted from the vis definition
        self._filters = [] # This filters are usually extracted from the vis definition.
        self._timeFilter = {} # Time filter. Usually extracted from the vis definition (Provided by the timebar)
        self._graphFilters = [] # Filters defined by the user to narrow visualization results in graph() 
        self._pickers = {} # Default pickers values for the visualization

    def auth(self, server, user, password):
        cred = user+':'+password
        key = base64.b64encode(cred.encode('ascii'))
        key = 'Basic ' + key.decode('ascii')
        self._conf['headers']['Authorization'] = key
        # Get the account
        if server:
            server.rstrip('/')
            self._serverURL = server
        self._account = rest.getUserAccount(self._serverURL, self._conf['headers'], user)
        self._user = user

    def __updateSourceFile(self):
        with open(SOURCES_JSON_FILE, 'w') as sc:
            json.dump(self._source_credentials, sc)

    def _oauth(self, user):
        # Ideally this should go within data_handler
        self._user = user
        if(os.path.exists(USERDATA_FILE)):
            datafile = open(USERDATA_FILE, 'rb')
            data = pickle.load(datafile)
            userdata = data.get(user, False)
            datafile.close()
            if userdata:
                self._account = userdata['accountId']
                self._token = userdata['token']
                key = "Bearer {}".format(userdata['token'])
                self._conf['headers']['Authorization'] = key

    def register(self, sourceName, dataframe): 
        """Creates a new Zoomdata source or updates an existing one. If the source exists all data will be
           replaced (overwrite) with the new data. The source structure (field_names/columns) will be preserved.
            Parameters:
                sourceName: The name of the source to be created / update.
                dataframe: Contains the data used to populate the source, commonly a pandas dataframe is used
        """
        self.__sourceData(sourceName, dataframe, True)

    def append(self, sourceName, dataframe): 
        """Updates a source by appending the new data to the existing one.
           Parameters:
                sourceName: The name of the source to update.
                dataframe: Contains the data used to populate the source, commonly a pandas dataframe is used
        """
        if(self._conf['headers']['Authorization']):
            sources = rest.getAllSources(self._serverURL, self._conf['headers'])
            if sourceName not in sources:  
                print('%s is not a valid source. Execute ZD.sources() to get a list of available sources' % sourceName)
            else:
                self.__sourceData(sourceName, dataframe, False)
        else:
            print('You need to authenticate: ZD.auth("user","password")')

    def __sourceData(self, sourceName, dataframe, replace): 
        if(self._conf['headers']['Authorization']):
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

            resp, upd = rest.createSourceFromData(self._serverURL, self._conf['headers'], \
                                            self._account, sourceName, df, urlParams, replace)
            if resp and upd:
                # Avoid using wrong (deprecated) keys in case an old source with the same name
                # existed. This is only for new sources
                self._source_id = rest.getSourceID(self._serverURL, self._conf['headers'], sourceName)
                acc_token = False if self._token == '' else self._token
                self._credentials = rest.getSourceKey(self._serverURL, self._conf['headers'], sourceName, token=acc_token)
                self._source = sourceName
                self._source_credentials.update({sourceName: [ self._credentials, self._source_id ]})
                self.__updateSourceFile()
                vis = rest.getSourceById(self._serverURL, self._conf['headers'], self._source_id)
                if vis:
                    self._source_charts = [v['name'] for v in vis['visualizations']]
                    self.__updateSourceFile()
        else:
            print('You need to authenticate: ZD.auth("user","password")')

    def sources(self):
        """ List the availables sources for the account"""
        if(self._conf['headers']['Authorization']):
            sources = rest.getAllSources(self._serverURL, self._conf['headers'])
            if sources:
                count = 1
                for s in sources:
                    print(str(count)+'. '+s)
                    count += 1
        else:
            print('You need to authenticate: ZD.auth("user","password")')


    #====== SET CHART TYPES FOR A VISUALIZATION IF IT DOES NOT HAVE IT ==========
    def setVisualization(self, name, definition={}):
        if(self._conf['headers']['Authorization']):
            # 1. First get the ID of the specific visualization
            if self._credentials:
                print('Checking allowed chart types...')
                if not (self._allowed_visuals):
                    self._allowed_visuals = rest.getVisualizationsList(self._serverURL, self._conf['headers'])
                visualsNames = [v['name'] for v in self._allowed_visuals]
                if name not in visualsNames:
                    print('Visualization type not found or not configured. Supported visualizations are:')
                    print('\n'.join(visualsNames))
                else:
                    visId = [v['id'] for v in self._allowed_visuals if v['name'] == name]
                    result = False
                    if name == 'Map: Markers':
                        result = vd.setMapMarkers(visId[0], definition, self._serverURL, \
                                                    self._conf['headers'], self._source_id)
                    elif name == 'Line & Bars Trend':
                        result = vd.setLineBarsTrend(visId[0], definition, self._serverURL, \
                                                    self._conf['headers'], self._source_id)
                    if result:
                        self._source_charts.append(name)
                    else:
                        print('Error: Probably the add/update feature is not supported yet for this chart type.')

            else:
                print('You must define a source before setting a new visualization')
        else:
            print('You need to authenticate: ZD.auth("user","password")')

            
    def source(self, nsource):
        """
        Allows to manually set up a new source for different operations just as fields() or getConnectionData()
        Parameters:
            - source: (String). The name of the source
        """
        #Set the source
        if not nsource:
            print('A source name must be specified')
            return False
        if(self._conf['headers']['Authorization']):
            #To avoid useless requests, check the local env to see if the source is registered
            credentials = False
            source_id = False
            if self._source_credentials.get(nsource, False): # If the source is allready registered
                credentials = self._source_credentials[nsource][0] # The key of the source
                source_id = self._source_credentials[nsource][1] # The id of the source

            #Check the source saved data match the one with zoomdata
            if(self._conf['headers']['Authorization']):
                check_source_id = rest.getSourceID(self._serverURL, self._conf['headers'], nsource)
            else:
                print('You need to authenticate: ZD.auth("user","password")')
                return False
            if not check_source_id:
                print('The requested source does not exists. To get all the active sources execute: ZD.sources()')
                return False
            #The source exists, but the saved and current ids don't match (deleted and recreated)
            if source_id != check_source_id:
                source_id = check_source_id
                credentials = False

            if not credentials: 
                acc_token = False if self._token == '' else self._token
                credentials = rest.getSourceKey(self._serverURL, self._conf['headers'], nsource, token=acc_token)
                if not credentials:
                    print('Some problems were found trying to set up this source, perhaps it was deleted from Zoomdata')
                    return False
            self._source = nsource
            self._credentials = credentials
            self._source_id = source_id
            self._source_credentials.update({nsource: [ self._credentials, self._source_id ]})
            vis = rest.getSourceById(self._serverURL, self._conf['headers'], self._source_id)
            if vis:
                self._source_charts = [v['name'] for v in vis['visualizations']]
                self.__updateSourceFile()

                # This is for the new syntax
                data = {
                        'source_name': nsource,
                        'source_id': source_id,
                        'source_charts': self._source_charts,
                        'source_key': credentials,
                        'headers': self._conf['headers'],
                        'url': self._serverURL,
                        'token': self._token or False,
                        'conf': self._conf
                        }
                return Source(data)

            else: # If not vis it means that source was deleted from zoomdata
                self._source_credentials.pop(nsource)
                self.__updateSourceFile()
                print('Some problems were found trying to set up this source, perhaps it was deleted from Zoomdata')
                return False 

        else:
            print('You need to authenticate: ZD.auth("user","password")')
            return False



    #====== PROPERTIES (DEFINED THIS WAY TO PROVIDE DOCSTRING) ===============
    @property
    def conf(self):
        """Dict: Configuration to create collections and sources. Uses specific Zoomdata configuration such as port and server for mongo connections, accounts Ids, authorization headers
        """
        return self._conf

    @conf.setter
    def conf(self, value):
        self._conf = value
        protocol = 'https' if self._conf['secure'] else 'http'
        self._serverURL = '%s://%s:%s%s' % (protocol, self._conf['host'], self._conf['port'], self._conf['path'])

