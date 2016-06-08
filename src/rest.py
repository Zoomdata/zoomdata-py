import urllib3
import json
http = urllib3.PoolManager()

def data(resp):
    return resp.data.decode('ascii')

class RestCalls(object):

    def createConnection(self, url, headers, accountID, connReq, connectionName):
        connReq['mongo']['name'] = connectionName
        body=json.dumps(connReq['mongo'])
        service = '/api/accounts/'+accountID+'/connections'
        print('Creating connection...')
        r = http.request('POST', url+service ,headers=headers, body=body)
        if r.status in [200, 201]:
            print('Connection created')
            return data(r)
        else:
            print(data(r))
        return False

    def createSource(self, url, headers, accountID, sourceName, connectionName, connReq, sourceReq):
        # Try to get the connection first in case it exists
        service = '/api/accounts/'+accountID+'/connections/name/'+connectionName
        r = http.request('GET', url+service, headers=headers)
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
            for l in links:
                if l['rel'] == 'sources':
                    url = l['href']
            if url:
                print('Good Url')
                sourceReq['name'] = sourceName
                sourceReq['sourceParameters']['collection']= sourceName;
                body=json.dumps(sourceReq)
                print('Creating source...')
                r = http.request('POST', url, headers=headers, body=body)
                if r.status in [200, 201]:
                    print('Source created')
                    return True
                else:
                    print(data(r))
        return False


    def getSourcesByAccount(self, url, headers, accountID):
        service = '/api/accounts/'+accountID+'/sources'
        r = http.request('GET', url+service ,headers=headers)
        resp= json.loads(data(r))
        resp = resp.get('data',False)
        sources = []
        if resp:
            count = 1
            for d in resp:
                print(str(count) +'. '+d['name'])
                count += 1
        else: 
            print(resp)

    def getVisualizationsList(self, url, headers):
        """ Get the list of all visualizations allowed by Zoomdata """
        service = '/service/visualizations'
        r = http.request('GET', url+service, headers=headers)
        if r.status in [200]:
            vis = [{'id': d['id'], 'name': d['name']} for d in json.loads(data(r))]
            return vis
        print(data(r))
        return False

    def getSourceById(self, url, headers, sourceId):
        service = '/service/sources/'+sourceId
        r = http.request('GET', url+service, headers=headers)
        if r.status in [200]:
            return json.loads(data(r))
        print(data(r))
        return False

    def updateSourceDefinition(self, url, headers, sourceId, body):
        service = '/service/sources/'+sourceId
        body=json.dumps(body)
        r = http.request('PATCH', url+service, headers=headers, body=body)
        if r.status in [200]:
            return True
        print(data(r))
        return False

