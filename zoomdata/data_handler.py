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
