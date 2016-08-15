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
import pickle

_fileName = '/.userdata.pkl'

def saveUserData(userdata):
    """
    This function saves the data sent from oauthenticator/zoomdata.py
    """
    _dataFile = os.path.expanduser('~'+userdata['name']) + _fileName
    if not os.path.exists(_dataFile):
        data = {}
    else:
        datafile = open(_dataFile, 'rb')
        data = pickle.load(datafile)
        datafile.close()
    datafile = open(_dataFile, 'wb')
    data.update({userdata['name']:userdata})
    pickle.dump(data, datafile)
    datafile.close()

def loadUserData(user):
    """
    Load the auth data for a user, if no user is specified all data will be returned
    """
    _dataFile = os.path.expanduser('~'+user) + _fileName
    datafile = open(_dataFile, 'rb')
    data = pickle.load(datafile)
    datafile.close()
    if user:
        return data.get(user, False)
    return {}
