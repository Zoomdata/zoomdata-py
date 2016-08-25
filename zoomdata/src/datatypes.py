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
import json
from datetime import datetime
FILTER_OPERATIONS= [# Containment
                    "IN",
                    "NOTIN",
                    # Comparison and equality
                    "LE",
                    "LT",
                    "GE",
                    "GT",
                    "EQUALS",
                    "NOTEQUALS",
                    # Range filter
                    "BETWEEN",
                    # Boolean filter
                    "AND",
                    "OR",
                    # Range filter
                    "TEXT_SEARCH", 
                    # Case sensitive
                    "EQUALSI"]

class Attribute(object):
    def __init__(self, name):
        self.__name = name
        self.__label = ""
        self.__limit = 1000
        self.__type = "ATTRIBUTE"
        self.__sort =  "count"
        self.__sortdir =  "DESC"
        self.__sortfunc = "SUM"
        self.__unit = ""
        
    def __repr__(self):
        attr = self.getval()
        return json.dumps(attr)

    def limit(self, limit):
        if not isinstance(limit, int):
            print('Incorrect value for the limit')
            return False
        self.__limit = limit
        return self

    def unit(self, unit):
        vals = ["MINUTE", "HOUR", "DAY", "WEEK", "MONTH", "YEAR"]
        if unit.upper() not in vals:
            values = ','.join(vals)
            print('Incorrect value for the unit(granularity): Try one of these: %s' % values)
            return False
        self.__unit = unit.upper()
        return self

    def dir(self, direction):
        vals = ['ASC','DESC','ALPHAB','REV-ALPHAB']
        if direction.upper() not in vals:
            values = ','.join(vals)
            print('Incorrect value for the direction: Try one of these: %s' % values)
            return False
        self.__sortdir = direction.upper()
        return self

    def sortby(self, metric):
        if not isinstance(metric, Metric):
            print('metric should be a Metric("name", "func") object')
            return False
        self.__sort = metric.getval()['name']
        self.__sortfunc = metric.getval()['func']
        return self

    def getval(self):
        attr = {'name': self.__name, 'type':'ATTRIBUTE', 'limit': self.__limit, 'sort':{}}
        if self.__label:
            attr.update({'label': self.__label})
        if  self.__unit:
            self.__sort = self.__name
            attr.update({'type': 'TIME', 'granularity':self.__unit})
        if 'ALPHAB' in self.__sortdir:
            self.__sort = self.__name
            self.__sortdir = 'ASC' if self.__sortdir == 'ALPHAB' else 'DESC'
            self.__sortfunc = False
        if self.__sort == 'count':
            self.__sortfunc = False
        attr['sort'].update({'name':self.__sort, 'dir':self.__sortdir})
        if self.__sortfunc:
            attr['sort'].update({'func':self.__sortfunc})
        return attr

            
class Metric(object):
    def __init__(self, name="count", func="SUM"):
        self.__name = name
        self.__func  = func
        
    def __repr__(self):
        attr = self.getval()
        return json.dumps(attr)

    def getval(self):
        metric = {'name': self.__name, 'func': self.__func}
        if self.__name is "count":
            metric['func'] = ""
        return metric


class Filter(object):
    def __init__(self, name):
        self.__name = name
        self.__operation = "IN"
        self.__values = []
    
    def __repr__(self):
        attr = self.getval()
        return json.dumps(attr)

    def operation(self, op):
        if op not in FILTER_OPERATIONS:
            print("Not a valid filter operation")
            return False
        self.__operation = op
        return self

    def values(self, *args):
        #TODO: Add support to other types of values depending on the operation
        if args and isinstance(args[0], list):
            self.__values = args[0]
        self.__values = list(args)
        return self

    def getval(self):
        return {
                'path': self.__name,
                'operation': self.__operation,
                'value': self.__values
                }

class TimeFilter(object):
    def __init__(self, name):
        self.__name = name
        self.__from = "IN"
        year = datetime.now().year
        self.__to = "+%s-12-31 12:58:00.000" % (str(year))

    def __repr__(self):
        attr = self.getval()
        return json.dumps(attr)

    def __formatdate(self, udate, to=False):
        a = "+2008-01-10 12:58:00.000"
        secs = ".00.000"
        hour = {"start":"00:00:00.000", "end":"12:58:00.000"}
        date = {"sm":"01", "em":"12", "sd": "01", "ed":"31"}
        parts = udate.split(" ")
        ymd = parts[0].split("-")
        fmt_date = ""
        if len(ymd) == 1:
            if not to: # Only the year was specified
                fmt_date = "%s-%s-%s %s" % (ymd[0], date['sm'], date['sd'], hour['start'])
            fmt_date = "%s-%s-%s %s" % (ymd[0], date['em'], date['ed'], hour['end'])
        elif len(ymd) == 2:
            if not to: # year-month 
                fmt_date = "%s-%s-%s %s" % (ymd[0], ymd[1], date['sd'], hour['start'])
            fmt_date = "%s-%s-%s %s" % (ymd[0], ymd[1], date['ed'], hour['end'])
        elif len(ymd) == 3:
            if not to: # year-month-day 
                fmt_date = "%s-%s-%s %s" % (ymd[0], ymd[1], ymd[2], hour['start'])
            fmt_date = "%s-%s-%s %s" % (ymd[0], ymd[1], ymd[2], hour['end'])
        if not '+' in fmt_date:
            fmt_date = '+' + fmt_date
        if len(parts) > 1 or 'start_of_data' in udate or 'end_of_data' in udate:
            return udate
        return fmt_date
    
    def start(self, start):
        if not isinstance(start, str):
            print('Start date should be a string')
            return False
        start = self.__formatdate(start)
        self.__from = start
        return self

    def to(self, to):
        if not isinstance(to, str):
            print('Stop date should be a string')
            return False
        to = self.__formatdate(to, True)
        self.__to = to
        return self

    def getval(self):
        return {
                'timeField': self.__name,
                'from': self.__from,
                'to': self.__to
                }
