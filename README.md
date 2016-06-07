# Jupyter - ZDvis

ZDVIS is a python3 module that allows to render Zoomdata visualizations into your Jupyter notebooks (http://jupyter.org) using the public Zoomdata SDK.

## Python dependencies

The following python modules are required to use ZDvis: urllib3, json, base64, pymongo

## Installation
Clone this repo or download it and copy it into your notebooks folder
```
cd ~/.jupyter/notebooks   #or your notebooks folder
git clone https://github.com/Zoomdata/ZDvis
```
Then start your jupyter server

## Usage

First you need to import from the module the ZD object.

```
from zdvis import ZD
```

ZD is a python object that allows you to perform different actions using the Zoomdata SDK:

##### Getting ZD object help
You can inspect attributes and methods from the ZD object as well as get the help for each one of them as in any normal Ipython session: by pressing the `tab` key as autocomplete for `ZD.` and adding a question mark `?` at the end of a attr/method to get the docstring.


##### Authentication
Some funtions require to be authenticated (listSources, createSource)
```
ZD.auth("username", "password")
```

##### Visualizations
To render a visualization you need to specify the source that you want to use:

```
ZD.source = 'Source name'
ZD.render()
```
To list the available sources (requires authentication):
```
ZD.listSources()
```
##### Source creation
New sources can be created on new or existing connections. As data it accepts a Pandas dataframe or if not dataframe is specified
a mongo collection with the same name that `sourceName` will be used instead. Use `ZD.createSource?` for more details

```
ZD.createSource(sourceName, dataframe, handler, connectionName)
```

##### Other configurations
ZDvis allows different configurations by changing ZD attributes. For example if you want to change the visualization chart type
```
ZD.chart = 'Heat Map'
```

or change/see the mongo server configuration:
```
ZD.conf['mongoServer']
ZD.conf['mongoPort']
ZD.conf['mongoSchema']
```
