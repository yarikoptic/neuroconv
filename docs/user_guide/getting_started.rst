Installation
============

NeuroConv is pip installable, and this is the recommended route for most users. To get started, run

.. code-block:: bash

    pip install neuroconv

If you are a developer, you will want to clone the repo and install locally

.. code-block:: bash

    git clone https://github.com/catalystneuro/neuroconv
    cd neuroconv
    pip install -e .

NeuroConv has many soft dependencies. These dependencies are not installed by default, and most users will only require
a small subset of them, but if you want to run the test suite you will need all of them. To install them, run

.. code-block:: bash

    pip install -e .[full]