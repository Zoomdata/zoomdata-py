#/usr/bin/python3
from .config import paths, applicationConfig, queryConfig, credentials
from .jsbuilder import JSBuilder
from IPython.display import HTML, IFrame
js = JSBuilder()

class ZDVisualization(object):

    """ ZDVisualization puts together all the javascript pieces
    needed to create a connection with the ZD SDK and fecth 
    the requested data. It finally renders the html and js into
    the notebook output dom through the HTML object """

    def __init__(self):
        """ To ensure maximum flexibility for the visualization configuration
        here must be setted all values that may change """
        self.width = 800
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
        visLocation = js.var('visLocation','document.getElementById("'+visualDiv+'")')
        zdSDK = self.__connectionPromise()
        p = visLocation + zdSDK
        param = js.createFunc(params=injlist, body=p, anon=True)
        return 'require(%s,%s)' % (js.s(injlist), param)

    def __getVisualization(self):
        """Set up of the final code snippet to be rendered"""
        w, h = self.width, self.height
        visualDiv = 'visual%s' % (str(self.renderCount))
        requirejs = '<script src="https://cdnjs.cloudflare.com/ajax/libs/require.js/2.2.0/require.min.js"></script>'
        htmlcode = '<div id="%s" style="width:%spx; height:%spx; top:20%%"></div>' % (visualDiv, str(w), str(h))
        jscode = '<script type="text/javascript">\n%s %s \n</script>' % (self.__setRequireConf(), self.__setRequire())
        html = htmlcode + jscode
        iframe = """<iframe 
                        srcdoc='<div>%s %s</div>' 
                        src='' 
                        width='%s' 
                        height='%s' 
                        sandbox='allow-scripts' 
                        frameborder='0'>
                    </iframe>
        """ % (requirejs, html, str(w+40), str(h+20) )
        return iframe, htmlcode, jscode

    def visualize(self):
        iframe = self.__getVisualization()[0]
        self.renderCount += 1
        return HTML(iframe)

    def getHTML(self):
        try:
            import jsbeautifier
            iframe, html, jscode = self.__getVisualization()
            jscode = jsbeautifier.beautify(jscode)
            print (html+'\n'+jscode)
        except ImportError:
            print ('Module jsbeautifier is required for this feature')







        
