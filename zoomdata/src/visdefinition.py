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
from .rest import RestCalls
import os
import json
rest = RestCalls()

class VisDefinition(object):
    """ VisDefinition creates or updates new visual definitions for a given
    source """

    def setMapMarkers(self, visId, definition, url, headers, obj_credentials):
        path = os.path.dirname(os.path.realpath(__file__))
        lat = definition.get('lat',False)
        lon = definition.get('long',False)
        if not lat or not lon:
            msg = "Definition dictionary for 'Map: Markers' must be as follow: "
            print(msg+"{'lat':'latitude_field_name', 'long':'longitude_field_name'}")
        else:
            visual_definition = {}
            with open(path+'/static/js/visdef/map_markers.json', 'r') as v: 
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

    def setLineBarsTrend(self, visId, definition, url, headers, obj_credentials):
        path = os.path.dirname(os.path.realpath(__file__))
        field = definition.get('field',False)
        limit = definition.get('limit',1000)
        order = definition.get('dir','asc')
        y1 = definition.get('y1',False)
        y2 = definition.get('y2',False)
        if not field:
            msg = "Definition dictionary for 'Line & Bars Trend' can be as follow: "
            print(msg+"{'field':'time_field_name', 'limit':values_limit, 'dir':'asc/desc', 'y1':'default_y1_value', 'y2':'..'}")
            print('Except for field, any other value is optional')
        else:
            visual_definition = {}
            with open(path+'/static/js/visdef/line_bars_trend.json', 'r') as v: 
                visual_definition = json.load(v)
                trend_attr = "{\"name\":\"%s\",\"limit\":%d,\"sort\":{\"dir\":\"%s\",\"name\":\"%s\"}}"
                trend_attr = trend_attr % (field, limit, order, field)
                visual_definition['visId'] = visId
                visual_definition['source']['variables']['Trend Attribute'] = trend_attr
                if(y1):
                    visual_definition['source']['variables']['Y1 Axis'] = y1
                if(y2):
                    visual_definition['source']['variables']['Y2 Axis'] = y2
            #Get the source by id
            print('Getting the source definition...')
            source_def = rest.getSourceById(url, headers, obj_credentials)
            if source_def:
                #Check if this source already has a map marker
                in_source = False
                for v in source_def['visualizations']:
                    if v['name'] == 'Line & Bars Trend':
                        v['source']['variables']['Trend Attribute'] = trend_attr# Update it
                        if(y1):
                            visual_definition['source']['variables']['Y1 Axis'] = y1
                        if(y2):
                            visual_definition['source']['variables']['Y2 Axis'] = y2
                        in_source = True
                if not in_source:
                    source_def['visualizations'].append(visual_definition)
                print('Setting the source definition with the new visualization...')
                if(rest.updateSourceDefinition(url, headers, obj_credentials, source_def)):
                    print('Done')
                    return True
                return False
