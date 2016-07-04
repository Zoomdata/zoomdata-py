# Jupyter - ZDvis

ZDVIS is a python3 module that allows to perform different operations using the public Zoomdata SDK straight into your Jupyter notebooks (http://jupyter.org) such as render visualizations, source data fetching, sources analysis, etc.

## Python dependencies

The following python modules are required to use ZDvis: urllib3, json, base64, websockets.

## Installation
Clone this repo or download it and install it as a normal python3 module
```
git clone https://github.com/Zoomdata/ZDvis
cd zdvis
sudo python3 setup.py install
```
Then start your jupyter server

## Usage

The entire functionality of the Zdvis module comes from the ZD object which is the main interface for every supported Zoomdata services within this module. In order to be able to use the ZD methods, you must authenticate first using one of this ways:

##### 1. Basic auth

This type of authentication is focused mainly when you want to use the ZD module in your local Jupyter server. First you need to import from the module the ZD object into your notebook as any other python module and then specify some valid zoomdata credentials (for testing you may use zoomdata:zoomdata) using the auth() method from the ZD object.

```
from zdvis import ZD
ZD.auth("zoomdataserver","username", "password")
```


##### 2. Oauth2
This type of authentication is mainly focused on a multi-user environment. Is supported by the Zoomdata oauth2 service and is only available using the [zd-jupyterhub-oauth](https://github.com/Zoomdata/zd-jupyterhub-oauth2) project. Using this authentication type, once a notebook is opened or created the ZD object will be automatically available with the respective user credentials. Please refer to the project page for more information.


#### Getting ZD object help
You can inspect attributes and methods from the ZD object as well as get help for each one of them as in any normal Ipython session: by pressing the `tab` key as autocomplete for `ZD.` and adding a question mark `?` at the end of a attr/method to get the docstring.


#### Visualizations

Visualizations are one of the main and awsome things you can do width this module. It allows you to bring almost any available visualization from a Zoomdata source into your notebook. There are different ways to render visualizations:

##### graph()

This method takes two required parameters: the source and the chart type. It also accepts some other configuration options as default pickers and filters. Example of basic usage:

```
ZD.graph('Ticket Sales','Bars')
```

Graph will complaint in case the chart type is incorrect, and will give the available charts for that specific source. There are also some shortcuts for the most common visualizations:

```
ZD.pie()
ZD.donut()
ZD.bars()
ZD.kpi()
ZD.treeMap()
ZD.heatMap()
```

These shortcuts, takes as parameters the same that the graph() function except for the chart type. They also don't need the source parameter if the graph() or the setSource() functions were used before as the will use the last used source.


#### Working with sources


##### sources()

This is the first utility to work with sources This method retrieves the list of available sources at zoomdata that you can work withr. Takes no parameter

##### setSource()
Set a source to work with. Takes the source name as parameter.

##### fields()
Retrieves the fields of the source specified by setSource() or the last one used by the graph() method.

##### getData()
This methods retrieves a pandas dataframe object containing data from the given source. It takes as a required parameter the source. It also accepts the fields to retrieve and the limit of rows. By the default all the fields will be fetched with a limit of 1,000,000 rows.

```
ZD.getData('Ticket Sales',['catname','venuestate'],100)
```

##### first()
This is a shortcut to get only the first row from a source. Takes as parameter the source and optionally the fields. Is the same as specifiying getData with limit 1.

##### register()
This will allow you to create a new Zoomdata source from a dataframe. Commonly a pandas dataframe is used.

```
ZD.register('My source name', dataframe_object)
```

Once the source is created you can visualize it as any other source.

