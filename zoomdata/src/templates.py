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
class Template(object):

    def __init__(self):
        # RequireJS CDN
        self.requirejs = '<script src="https://cdnjs.cloudflare.com/ajax/libs/require.js/2.2.0/require.min.js"></script>'
        self.confirmcss   ='<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/jquery-confirm/2.5.1/jquery-confirm.min.css" type="text/css" media="screen"/>'
        self.bootstrapcss = '<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css" type="text/css" media="screen"/>'
        self.styleTags = '<style type="text/css" media="screen">%s</style>'
        #Iframe where everything will be rendered
        self.iframe = """
                        <script type="text/javascript">var kernel = IPython.notebook.kernel</script>
                        <iframe 
                            srcdoc='<div align="center">%s %s</div>' 
                            src='' 
                            width='%s' 
                            height='%s' 
                            frameborder='0'>
                        </iframe> """ 

        self.loadmsg = '<p id="load-message" style="margin-top:10px" align="center">Loading visualization...</p>'

        # Output messages for getData
        self.logdata = "<div id='fetch%d'></div><div id='done%d'></div>"

        # Javascript tags to enclose all the js code
        self.scriptTags = '<script type="text/javascript">%s</script>' 

        # Div where the chart is rendered (by echartjs)
        self.divChart = '<div id="%s" class="zd medium" style="width:%spx; height:%spx; top:20%%"></div>'

        # Container div for the filters (metric, dimension) drop-downs
        self.divFilters = '<div id="pickers" style="display:inline-block;margin-top:5px" align="center"></div>' 
