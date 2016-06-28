import os
import pickle

def save_data(userdata):
    """
    This function saves the data sent from oauthenticator/zoomdata.py
    """
    if not os.path.exists('userdata.pkl'):
        data = {}
    else:
        datafile = open('userdata.pkl', 'rb')
        data = pickle.load(datafile)
        datafile.close()
    datafile = open('userdata.pkl', 'wb')
    data.update({userdata['name']:userdata})
    pickle.dump(data, datafile)
    datafile.close()
