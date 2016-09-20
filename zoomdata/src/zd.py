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
from .config import *
from IPython.display import display, HTML

rest = RestCalls()
home_dir = os.path.expanduser('~')

SOURCES_JSON_FILE = home_dir + "/.sources.json"
USERDATA_FILE = home_dir + "/.userdata.pkl"

class Zoomdata(object):

    """ Works as an API connector with the Zoomdata services and SDK
    allowing to bring visualizations, work with sources, fetch and send data..
    """

    def __init__(self):
        self._conf = config
        protocol = 'https' if config['secure'] else 'http'
        self._serverURL = '%s://%s:%s%s' % (protocol, config['host'], config['port'], config['path'])
        self._source_credentials = {} # Saves the pair key,id for the used sources

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

    def auth(self, user, password, host=False):
        """
        Authenticates a user to allow the communication between the module and Zoomdata
        Parameters:
            - user: (String) A valid user from zoomdata
            - password: (String) 
            - host (String) Optional. The server url where the zoomdata server is located. If no specified default configuration
                            will be used.
        """
        cred = user+':'+password
        key = base64.b64encode(cred.encode('ascii'))
        key = 'Basic ' + key.decode('ascii')
        self._conf['headers']['Authorization'] = key
        if host:
            host.rstrip('/')
            self._serverURL = host 
        self._account = rest.getUserAccount(self._serverURL, self._conf['headers'], user)
        if self._account:
            self._user = user

    def __updateSourceFile(self):
        with open(SOURCES_JSON_FILE, 'w') as sc:
            json.dump(self._source_credentials, sc)

    def _oauth(self, user):
        # Ideally this should go within data_handler
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
                self._user = user

    def register(self, sourceName, dataframe): 
        """Creates a new Zoomdata source or updates an existing one. If the source exists all data will be
           replaced (overwrite) with the new data. The source structure (field_names/columns) will be preserved.
            Parameters:
                sourceName: The name of the source to be created / update.
                dataframe: Contains the data used to populate the source, commonly a pandas dataframe is used
        """
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
                                        self._account, sourceName, df, urlParams, True)
        if resp and upd:
            # Avoid using wrong (deprecated) keys in case an old source with the same name
            # existed. This is only for new sources
            source_id = rest.getSourceID(self._serverURL, self._conf['headers'], sourceName)
            acc_token = False if self._token == '' else self._token
            source_key = rest.getSourceKey(self._serverURL, self._conf['headers'], sourceName, token=acc_token)
            self._source_credentials.update({sourceName: [ source_key, source_id ]})
            self.__updateSourceFile()
            vis = rest.getSourceById(self._serverURL, self._conf['headers'], source_id)
            if vis:
                self.__updateSourceFile()

    def sources(self):
        """ List the availables sources for the account"""
        if(self._user):
            sources = rest.getAllSources(self._serverURL, self._conf['headers'])
            if sources:
                return pd.DataFrame(sources,columns=['Name'])
        else:
            print('You need to authenticate: ZD.auth("user","password")')

    def source(self, nsource):
        """
        Returns a Source object as a representation for the given source
        Parameters:
            - source: (String). The name of the source
        """
        #Set the source
        if not nsource:
            print('A source name must be specified')
            return False
        if(self._user):
            #To avoid useless requests, check the local env to see if the source is registered
            credentials = False
            source_id = False
            if self._source_credentials.get(nsource, False): # If the source is allready registered
                source_key = self._source_credentials[nsource][0] # The key of the source
                source_id  = self._source_credentials[nsource][1] # The id of the source

            #Check the source saved data match the one with zoomdata
            check_source_id = rest.getSourceID(self._serverURL, self._conf['headers'], nsource)
            if not check_source_id:
                print('The requested source does not exists. To get all the active sources execute: ZD.sources()')
                return False
            #The source exists, but the saved and current ids don't match (deleted and recreated)
            if source_id != check_source_id:
                source_id = check_source_id
                credentials = False

            if not credentials: 
                acc_token = False if self._token == '' else self._token
                source_key= rest.getSourceKey(self._serverURL, self._conf['headers'], nsource, token=acc_token)
                if not source_key:
                    print('Some problems were found trying to set up this source, perhaps it was deleted from Zoomdata')
                    return False
            self._source_credentials.update({nsource: [ source_key, source_id ]})
            vis = rest.getSourceById(self._serverURL, self._conf['headers'], source_id)
            if vis:
                source_charts = [v['name'] for v in vis['visualizations']]
                self.__updateSourceFile()

                # This is for the new syntax
                data = {
                        'conf': self._conf,
                        'source_name': nsource,
                        'source_id': source_id,
                        'source_charts': source_charts,
                        'source_key': source_key,
                        'headers': self._conf['headers'],
                        'url': self._serverURL,
                        'token': self._token or False,
                        'account': self._account
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

