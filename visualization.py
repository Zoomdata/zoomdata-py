#/usr/bin/python3
from .config import paths, applicationConfig, queryConfig, credentials
from .jsbuilder import JSBuilder
from IPython.display import HTML, IFrame
from jinja2 import Template
js = JSBuilder()

class ZDVisualization(object):

    """ ZDVisualization puts together all the javascript pieces
    needed to create a connection with the ZD SDK and fecth 
    the requested data. It finally renders the html and js into
    the notebook output dom through the HTML object """

    def __init__(self):
        """ To ensure maximum flexibility for the visualization configuration
        here must be setted all values that may change """
        self.width = 900
        self.height = 400
        self.renderCount = 0 #To render a different chart each time
        self.paths = paths
        self.appConfig = applicationConfig
        self.query = queryConfig
        self.credentials =credentials
        self.visual = { 'source': {'name': 'Real Time Sales'},
                        'visualization': 'Bars',
                        'variables': {}
                        }

    def __setRequireConf(self):
        #Set the require configuration part
        return 'require.config({paths:%s});' % js.s(self.paths)

    def __createClient(self):
        credentials = {
                'credentials': self.credentials,
                'application': self.appConfig,
                }
        params = js.s(credentials)
        return 'ZoomdataSDK.createClient(%s)' % (params)

    def __connectionPromise(self):
        """Returns the string associated to the 
        promise that connects with ZD and creates the visualization"""
        prom = self.__createClient()
        p ='window.client = client; return(client)'
        then = '.then(%s)' % (js.createFunc(params='client',body=p, anon=True))
        visualconf = {'element':'%s', 'config': self.query}
        visualconf.update(self.visual)
        p = js.s(visualconf)
        p = js.setVars(p, 'visLocation') #set the element for echarts rendering
        done = '.done(%s);' % (js.createFunc(params='result',body='window.viz = result', anon=True))
        p = 'client.visualize(%s)%s' % (p, done)
        then1 = '.then(%s);' % (js.createFunc(params='client',body=p, anon=True))
        return prom+then+then1

    def __setRequire(self):
        """ Render the require wrapper with ZDSDK and jquery dep injection."""
        injlist = ['ZoomdataSDK','jquery']
        visualDiv = 'visual%s' % (str(self.renderCount))
        visLocation = js.var('visLocation','document.getElementById("'+visualDiv+'");')
        zdSDK = self.__connectionPromise()
        p = visLocation + zdSDK
        param = js.createFunc(params=injlist, body=p, anon=True)
        return 'require(%s,%s)' % (js.s(injlist), param)

    def __getVisualization(self):
        visualDiv = 'visual%s' % (str(self.renderCount))
        h = str(self.height)
        w = str(self.width)
        htmlcode = "<div id='"+visualDiv+"' style='width:"+w+"px; height:"+h+"px; top:20%; float:left'></div>"
        jscode = '''<script type="text/javascript"> %s %s </script>''' \
                    % (self.__setRequireConf(), self.__setRequire())
        return htmlcode, jscode

    def visualize(self):
        # print(htmlcode + jscode)
        htmlcode, jscode = self.__getVisualization()
        self.renderCount += 1
        return HTML(htmlcode + jscode)

    def getHTML(self):
        htmlcode, jscode = self.__getVisualization()
        htmlfull = (htmlcode + jscode).replace('\\','')
        print (htmlfull)







        
