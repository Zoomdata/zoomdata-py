# Jupyter - ZDvis

ZDVIS is a python module that allows to render Zoomdata visualizations into your Jupyter notebooks using the public Zoomdata SDK.

## Installation

Clone this repo or download it and copy it into your notebooks folder
```
cd ~/.jupyter/notebooks   #your notebooks folder
git clone https://github.com/Zoomdata/ZDvis
```
Then start your jupyter server

## Usage

First you need to import the module

```
from zdvis import ZD
```

ZD is a python object contaning the configurations to render a ZD visualization. By default it is using the 'Real Time Sales' data sources.

To render a visualization:

```
ZD.visualize()
```

To change the visualization chart type
```
ZD.visual['visualization'] = 'Heat Map'
```

You can inspect the differents ZD attributes by pressing the `tab` key as autocomplete for `ZD.`
