from setuptools import setup, find_packages

setup(
        name = 'zdvis',
        version = '0.0.1',
        packages = find_packages(),
        install_requires=[ 'pandas', 'urllib3', 'websockets'],
        author = 'Aktiun',
        keywords=['zdvis','aktiun','zoomdata','jupyter','jupyterhub'],
        author_email = 'eduardo@aktiun.com',
        url = 'https://github.com/Zoomdata/ZDvis',
        description = 'Integrates Zoomdata visualizations into Jupyter notebooks',
        include_package_data=True,
        )
