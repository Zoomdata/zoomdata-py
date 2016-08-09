import urllib3
from urllib3.exceptions import MaxRetryError
import json
from urllib.parse import quote
urllib3.disable_warnings()
http = urllib3.PoolManager()

TIMEOUT_MSG = '''
The token for this session has expired, please log out and log in again. \n
And once logged in make sure to shutdown your notebook before starting it by checking\n
the notebook and clicking the shutdown button on the menu.
'''

def data(resp):
    return resp.data.decode('ascii')

class RestCalls(object):

    def createConnection(self, url, headers, accountID, connReq, connectionName):
        connReq['mongo']['name'] = connectionName
        body=json.dumps(connReq['mongo'])
        service = '/api/accounts/'+accountID+'/connections'
        print('Creating connection...')
        try:
            r = http.request('POST', url+service ,headers=headers, body=body)
        except MaxRetryError:
            print(TIMEOUT_MSG)
            return False
        if r.status in [200, 201]:
            print('Connection created')
            return data(r)
        else:
            print(data(r))
        return False

    def createSource(self, url, headers, accountID, sourceName, connectionName, connReq, sourceReq):
        # Try to get the connection first in case it exists
        service = '/api/accounts/'+accountID+'/connections/name/'+connectionName
        try:
            r = http.request('GET', url+service, headers=headers)
        except MaxRetryError:
            print(TIMEOUT_MSG)
            return False
        if r.status in [200]:
            connResponse = data(r)
        elif r.status in [403, 404]:
            connResponse = self.createConnection(url, headers, accountID, connReq, connectionName)
        else:
            print(data(r))
            return False
        # If a valid connection response is available
        if connResponse:
            links = json.loads(connResponse)['links']
            url = False
            url = [l['href'] for l in links if l['rel'] == 'sources']
            if url:
                print('Good Url')
                sourceReq['name'] = sourceName
                sourceReq['sourceParameters']['collection']= sourceName;
                body=json.dumps(sourceReq)
                print('Creating source...')
                r = http.request('POST', url[0], headers=headers, body=body)
                if r.status in [200, 201]:
                    print('Source created')
                    return True
                else:
                    print(data(r))
        return False

    def getUserAccount(self, url, headers, user):
        service = '/api/users/username/'+user
        try:
            r = http.request('GET', url+service ,headers=headers)
        except MaxRetryError:
            print(TIMEOUT_MSG)
            return False
        if r.status in [200]:
            resp= json.loads(data(r))
            href = [l['href'] for l in resp['links'] if l['rel'] == 'account']
            # https://server:port/zoomdata/api/accounts/56e9669ae4b03818a87e452c
            return href[0].split('/')[-1]
        print(data(r))

    def getSourcesByAccount(self, url, headers, accountID):
        service = '/api/accounts/'+accountID+'/sources'
        try:
            r = http.request('GET', url+service ,headers=headers)
        except MaxRetryError:
            print(TIMEOUT_MSG)
            return False
        resp= json.loads(data(r))
        resp = resp.get('data',False)
        if resp:
            return [d['name'] for d in resp]
        else: 
            print(resp)
            return False

    def getAllSources(self, url, headers):
        service = '/service/sources?fields=name'
        try:
            r = http.request('GET', url+service ,headers=headers)
        except MaxRetryError:
            print(TIMEOUT_MSG)
            return False
        resp= json.loads(data(r))
        if resp:
            return [d['name'] for d in resp]
        else: 
            print(resp)
            return False

    def getVisualizationsList(self, url, headers={}, token=False):
        """ Get the list of all visualizations allowed by Zoomdata """
        service = '/service/visualizations'
        if token:
            service += '?access_token='+token
        try:
            r = http.request('GET', url+service, headers=headers)
        except MaxRetryError:
            print(TIMEOUT_MSG)
            return False
        if r.status in [200]:
            vis = [{'id': d['id'], 'name': d['name'], 'type':d['type']} for d in json.loads(data(r))]
            return vis
        print(data(r))
        return False

    def getSourceById(self, url, headers, sourceId):
        service = '/service/sources/'+sourceId
        try:
            r = http.request('GET', url+service, headers=headers)
        except MaxRetryError:
            print(TIMEOUT_MSG)
            return False
        if r.status in [200]:
            return json.loads(data(r))
        print(data(r))
        return False

    def getSourceKey(self, url, headers, sourceName, print_error=True, token=False):
        # This method will be useless once oauth be implemented
        service = '/service/sources/key?source='+sourceName.replace(' ','+')
        if token:
            service += '&access_token='+token
        try:
            r = http.request('GET', url+service ,headers=headers)
        except MaxRetryError:
            print(TIMEOUT_MSG)
            return False
        if r.status in [200]:
            resp = json.loads(data(r))
            return resp['id']
        if print_error:
            print(data(r))
        return False

    def getSourceID(self, url, headers, sourceName, printError = True, token = False):
        # https://pubsdk.zoomdata.com:8443/zoomdata/service/sources?fields=name&access_token=
        service = '/service/sources?fields=name'
        if token:
            service += '&access_token='+ token
        try:
            r = http.request('GET', url+service, headers=headers)
        except MaxRetryError:
            print(TIMEOUT_MSG)
            return False
        if r.status in [200]:
            resp= json.loads(data(r))
            for source in resp:
                if source['name'] == sourceName:
                    return source['id']
        if printError and r.status != 200:
            print(data(r))
        return False

    
    def createSourceFromData(self, url, headers, accountId, sourceName, df, urlParams={}, replace=False):
        # Creates or uses a source to populate it with data (from a dataframe)
        # Check if the source exists
        sourceId = self.getSourceID(url, headers, sourceName, printError=False)
        newSource = False
        if not sourceId:
            newSource = True
            print('Creating source "'+sourceName+'"...')
            service = '/api/accounts/'+accountId+'/sources/file'
            body = {'name': sourceName, 'sourceParameters':{}}
            #Create the source
            #https://pubsdk.zoomdata.com:8443/zoomdata/api/accounts/56e9669ae4b03818a87e452c/sources/file
            try:
                r = http.request('POST', url+service, headers=headers, body=json.dumps(body))
            except MaxRetryError:
                print(TIMEOUT_MSG)
                return False, False
            if r.status in [200, 201]:
                resp = json.loads(data(r))
                href = [l['href'] for l in resp['links'] if l['rel'] == 'self']
                # https://server:port/zoomdata/api/sources/
                sourceId = href[0].split('/')[-1]
                print('Source with id "'+sourceId+'" sucessfully created')
            else:
                print(data(r))
                return False, False
        else:
            if replace: #Source data will be replaced instead of appended
                print('Cleaning data from "'+sourceName+'"...')
                service = '/service/sources/data/'+sourceId
                try:
                    r = http.request('DELETE', url+service, headers=headers)
                except MaxRetryError:
                    print(TIMEOUT_MSG)
                    return False, False
        #Populate the source with the specified data
        print('Populating source with new data...')
        service='/api/sources/'+sourceId+'/data?'
        param_format = '%s=%s'
        params_list = []
        for param in urlParams:
            p = param_format % (param, quote(urlParams[param]))
            params_list.append(p)
        service += '&'.join(params_list)
        try:
            r = http.request('PUT', url+service, headers=headers, body=df)
        except MaxRetryError:
            print(TIMEOUT_MSG)
            return False, False
        if r.status in [200, 201]:
            print('Done!')
            return True, newSource
        print(data(r))
        return False, False

    def updateSourceDefinition(self, url, headers, sourceId, body):
        service = '/service/sources/'+sourceId
        body=json.dumps(body)
        try:
            r = http.request('PATCH', url+service, headers=headers, body=body)
        except MaxRetryError:
            print(TIMEOUT_MSG)
            return False
        if r.status in [200]:
            return True
        print(data(r))
        return False

    def getDashboardData(self, url, dashboardId, token):
        service = '/service/bookmarks/%s?access_token=%s' % (dashboardId, token)
        try:
            r = http.request('GET', url+service) 
        except MaxRetryError:
            print(TIMEOUT_MSG)
            return False
        if r.status in [200]:
            print(r)
            resp= json.loads(data(r))
            return resp
        print(data(r))
        return False
