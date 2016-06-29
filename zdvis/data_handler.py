import os
import pickle

_dataFile = '/var/userdata.pkl'
        
def save_data(userdata):
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

def load_data():
    datafile = open(_dataFile, 'rb')
    data = pickle.load(datafile)
    datafile.close()
    return data
