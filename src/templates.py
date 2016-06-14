class Template(object):

    def __init__(self):
        # RequireJS CDN
        self.requirejs = '<script src="https://cdnjs.cloudflare.com/ajax/libs/require.js/2.2.0/require.min.js"></script>'
        self.jqueryjs = '<script src="https://ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js"></script>'
        self.zdclientjs= '<script src="https://pubsdk.zoomdata.com:8443/zoomdata/sdk/2.0/zoomdata-client.js"></script>'

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

        # Javascript tags to enclose all the js code
        self.scriptTags = '<script type="text/javascript">%s %s</script>' 

        # Select and option string formatters
        self.selectFmt = '''<span id="%s">%s</span>
                            <select id="%s" style="margin-right:20px; margin-left:5px">%s<select>'''
        self.optionFmt = '<option value="%s">%s</option>'

        # Div where the chart is rendered (by echartjs)
        self.divChart = '<div id="%s" class="zd chart" style="width:%spx; height:%spx; top:20%%"></div>'

        # Container div for the filters (metric, dimension) drop-downs
        self.divFilters = '<div style="display:inline-block;margin-top:5px" align="center">%s</div>' 
