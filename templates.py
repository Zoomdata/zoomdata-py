class Template(object):

    def __init__(self):
        self.requirejs = '<script src="https://cdnjs.cloudflare.com/ajax/libs/require.js/2.2.0/require.min.js"></script>'
        self.iframe = """<iframe 
                            srcdoc='<div align="center">%s %s</div>' 
                            src='' 
                            width='%s' 
                            height='%s' 
                            sandbox='allow-scripts' 
                            frameborder='0'>
                        </iframe> """ 
        self.selectFmt = '''<span>%s</span>
                            <select id="%s" style="margin-right:20px; margin-left:5px">%s<select>'''

        self.optionFmt = '<option value="%s">%s</option>'

        self.divChart = '<div id="%s" style="width:%spx; height:%spx; top:20%%"></div>'

        self.scriptTags = '<script type="text/javascript">%s %s</script>' 

        self.divFilters = '<div style="display:inline-block" align="center">%s</div>' 

        self.filterJS= ''' $("#%(s)s").change(function() {
                                %(s)s.name = $( "#%(s)s option:selected" )[0].value;
                                console.log(%(s)s.name)
                                console.log("Thread:",window.viz)
                                var accessor = window.viz["dataAccessors"]["%(attr)s"];
                                accessor.%(function)s(%(params)s)
                            });'''
