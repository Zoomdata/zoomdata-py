import os
import pickle

_dataFile = '/var/userdata.pkl'
        
def saveUserData(userdata):
    """
    This function saves the data sent from oauthenticator/zoomdata.py
    """
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

def loadUserData(user=False):
    """
    Load the auth data for a user, if no user is specified all data will be returned
    """
    datafile = open(_dataFile, 'rb')
    data = pickle.load(datafile)
    datafile.close()
    if user:
        return data.get(user, False)
    return data
