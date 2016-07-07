# Jupyter - ZDvis

ZDVIS is a python3 module that puts the power of Zoomdata straight into your Jupyter notebooks (http://jupyter.org).  For example, users can register pandas dataframes as Zoomdata sources, easily render many types of visualizations, and create pandas dataframes from any Zoomdata source.

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

The entire functionality of the Zdvis module comes from the ZD object which is the main interface for every supported Zoomdata services within this module. In order to be able to use the ZD methods, you must authenticate first using one of the following ways:

##### 1. Basic auth

This type of authentication is useful mainly when you want to use the ZD module in your local Jupyter server. First you need to import from the module the ZD object into your notebook as any other python module and then specify some valid zoomdata credentials (for testing you may use zoomdata:zoomdata) using the auth() method from the ZD object.

```
from zdvis import ZD
ZD.auth("zoomdataserver","username", "password")
```


##### 2. Oauth2
This type of authentication is mainly focused on a multi-user environment using the Zoomdata oauth2 service. Using this authentication type, when a notebook is opened or created the ZD object will be automatically available with the respective user credentials. Also it allows to to do all of this from within Zoomdata. Implementing this authentication requires the aid of other projects:

[Jupyterhub](https://github.com/Zoomdata/jupyterhub) 
[zd-jupyterhub-oauth](https://github.com/Zoomdata/zd-jupyterhub-oauth2) 

Please refer to the projects pages for more information on how to deploy the integration.

##### Note about using ZDvis with Zoomdata Oauth2

As oauth is token based and the token has an expiration time, users may need to log out from the jupyterhub session (same that Zoomdata session) and log back in after some period of inactivity to get a new token.  It's very important to note that this only affects the jupyterhub session. In order to also affect the notebook you were working on, you must shutdown this notebook by checking the notebook (it should be in green) and then clicking the 'shutdown' button on the menu bar. This will restart the notebook (your code won't be lost) and once you open it again, it will be aware of the new token.


#### Getting ZD object help
You can inspect attributes and methods of the ZD object by pressing the `tab` key as autocomplete for `ZD.` You can get help for them by adding a question mark `?` at the end of attributes and methods to obtain their docstring.


#### Visualizations

Visualizations are one of the main features.  This module allows you to bring many available visualization from a Zoomdata source into your notebook. There are different ways to render visualizations:

##### graph()

This method takes two required parameters: the source and the chart type. It also accepts some other configuration options as default pickers and filters. Example of basic usage:

```
ZD.graph('Ticket Sales','Bars')
```

Graph will complain if the chart type is incorrect and will print the available charts for the specific source. There are also some shortcuts for the most common visualizations:

```
ZD.pie()
ZD.donut()
ZD.bars()
ZD.kpi()
ZD.treeMap()
ZD.heatMap()
```

These shortcuts take the same parameters as the the graph() function except for the chart type. These shortcuts also don't need the source parameter if the graph() or the setSource() functions were used before as they will use the last used source.


#### Working with sources


##### sources()

This is the first function to use when working with sources.  It retrieves the list of available sources in Zoomdata for the authenticated user. Takes no parameters.

##### setSource()
It sets a source to work with. Takes the source name as parameter.

##### fields()
Retrieves the fields of the source specified by setSource() or the last one used by the graph() method.

##### getData()
This methods retrieves a pandas dataframe object with the data from the given Zoomdata source. It takes the Zoomdata source name as a required parameter.  It also accepts the fields to retrieve and the limit of rows. By the default all the fields will be fetched with a limit of 1,000,000 rows.

```
ZD.getData('Ticket Sales',['catname','venuestate'],100)
```

##### first()
This is a shortcut to get only the first row from a source.  It takes the Zoomdata source name as a required parameter and optionally the fields. It is equivalent to specifiying getData with limit 1.

##### register()
This function allows users to create a new Zoomdata source from a dataframe. Usually, this is a pandas dataframe.

```
ZD.register('My source name', dataframe_object)
```

Once the source is created you can visualize it as any other source.

