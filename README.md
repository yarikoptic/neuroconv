# nwbn-conversion-tools
Shared tools for converting data from various formats to NWB:N 2.0

## Installation
To clone the repository and set up a conda environment, do:
```
$ git clone https://github.com/NeurodataWithoutBorders/nwbn-conversion-tools
$ conda env create -f nwbn-conversion-tools/make_env.yml
$ source activate nwbn_conversion
```

Alternatively, to install **nwbn_conversion_tools** directly in an existing environment:
```
$ pip install git+https://github.com/NeurodataWithoutBorders/nwbn-conversion-tools
```

## GUI
After activating the correct environment, nwbn_conversion_tools GUI can be imported and run from the python interpreter.
```python
from nwbn_conversion_tools.gui.nwbn_conversion_gui import nwbn_conversion_gui

# YAML metafile
metafile = 'metafile.yml'

# Conversion module
conversion_module = 'conversion_module.py'

# Source files path
source_paths = {}
source_paths['source_file_1'] = {'type': 'file', 'path': ''}
source_paths['source_file_2'] = {'type': 'file', 'path': ''}

# Other options
kwargs = {'option_1': True, 'option_2': False}

nwbn_conversion_gui(
    metafile=metafile,
    conversion_module=conversion_module,
    source_paths=source_paths,
    kwargs_fields=kwargs,
)
```
[Here](https://github.com/NeurodataWithoutBorders/nwbn-conversion-tools/tree/master/nwbn_conversion_tools/gui) you can find templates for `metafile.yml` and `conversion_module.py`.


## optical physiology
### processing
* [CELLMax](https://github.com/NeurodataWithoutBorders/nwbn-conversion-tools/blob/master/nwbn_conversion_tools/ophys/processing/CELLMax/README.md)
