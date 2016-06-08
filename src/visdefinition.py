from .rest import RestCalls
import os
import json
rest = RestCalls()

class VisDefinition(object):

    def setMapMarkers(self, visId, definition, url, headers, obj_credentials):
        path = os.path.dirname(os.path.realpath(__file__))
        lat = definition.get('lat',False)
        lon = definition.get('long',False)
        if not lat or not lon:
            msg = "Definition dictionary for 'Map: Markers' must be as follow: "
            print(msg+"{'lat':'latitude_field_name', 'long':'longitude_field_name'}")
        else:
            visual_definition = {}
            with open(path+'/js/visdef/map_markers.json', 'r') as v: 
                visual_definition = json.load(v)
                lat_lon = "[{\"name\":\"%s\",\"limit\":100000},{\"name\":\"%s\",\"limit\":100000}]" % (lat, lon)
                visual_definition['visId'] = visId
                visual_definition['source']['variables']['Lat/Long'] = lat_lon
            #Get the source by id
            print('Getting the source definition...')
            source_def = rest.getSourceById(url, headers, obj_credentials)
            if source_def:
                #Check if this source already has a map marker
                in_source = False
                for v in source_def['visualizations']:
                    if v['name'] == 'Map: Markers':
                        v['source']['variables']['Lat/Long'] = lat_lon # Update it
                        in_source = True
                if not in_source:
                    source_def['visualizations'].append(visual_definition)
                print('Setting the source definition with the new visualization...')
                if(rest.updateSourceDefinition(url, headers, obj_credentials, source_def)):
                    print('Done')
                    return True
                return False
