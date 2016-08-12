from setuptools import setup, find_packages

setup(
        name = 'zoomdata',
        version = '0.1',
        packages = find_packages(),
        install_requires=[ 'pandas', 'urllib3', 'websockets'],
        author = 'Aktiun',
        keywords=['aktiun','zoomdata','jupyter','jupyterhub','zoomdata-py'],
        author_email = 'eduardo@aktiun.com',
        url = 'https://github.com/Zoomdata/zoomdata-py',
        description = 'Integrates Zoomdata visualizations into Jupyter notebooks',
        include_package_data=True,
        )
