from distutils.core import setup
setup(
        name = 'zdvis',
        version = '1.0.0',
        packages = ['zdvis','zdvis/src'],
        package_data={'js': ['zdvis/src/js/*'], 'visdef': ['zdvis/src/js/visdef/*'], 'render':['zdvis/src/js/render/*']},
        author = 'Aktiun',
        author_email = 'eduardo@aktiun.com',
        url = 'https://github.com/Zoomdata/ZDvis',
        description = 'Integrates Zoomdata visualizations into Jupyter notebooks'
        )
