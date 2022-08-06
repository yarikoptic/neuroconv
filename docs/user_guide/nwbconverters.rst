NWBConverter
============

It is common have multiple different data sources you want to combine into a single NWB file. This can occur when
there are different acquisition systems running simultaneously or if you want to add combine the raw data and the
output of processing into a single NWB file. The :py:class:`NWBConverter` class  allows you to combine multiple
:py:class:`DataInterface` types together to support an entire multi-source experiment configuration.

1. Define a Custom Class
------------------------
Unlike :py:class:`DataInterface`
classes, where there are several pre-built options ready to go, :py:class:`NWBConverter` classes are specific to an entire
experiment configuration, which is unique to each experiment, so you must define a custom :py:class:`NWBConverter` class to
fit your specific experiment and data processing configuration.

Here is an example of how to define a basic custom :py:class:`NWBConverter` class:

.. code-block:: python

    from neuroconv import (
        NWBConverter,
        BlackrockRecordingExtractorInterface,
        PhySortingInterface
    )

    class ExampleNWBConverter(NWBConverter):
        data_interface_classes = dict(
            BlackrockRecording=BlackrockRecordingExtractorInterface,
            PhySorting=PhySortingInterface
        )

All :py:class:`NWBConverter` descendants must define a :py:attr:`data_interface_classes` dictionary, a class
attribute that specifies what :py:class:`DataInterface` classes it will use. The above example defines a bare-bones
custom :py:class:`NWBConverter` that combines raw voltage data from a Blackrock format with spike sorting output from
Phy.

2. Initialization
-----------------
Next, construct an object of this class by initializing it with ``source_data``, a dictionary where the keys are the
same as the keys of ``data_interface_classes`` and the values are input arguments for the constructors of each of those
:py:class:`DataInterface` classes.

.. code-block:: python

    source_data = dict(
        BlackrockRecording=dict(
            file_path="raw_dataset_path"
        ),
        PhySorting=dict(
            folder_path="sorted_dataset_path"
        )
    )

    converter = ExampleNWBConverter(source_data)


To get the form of source_data, run :meth:`.BaseDataInterface.get_source_schema`, which returns the :ref:`source
schema <source_schema>` as a JSON-schema-like dictionary informing the user of the required and optional input
arguments to the downstream readers.

Constructing this ``converter`` creates instances of each of the underlying :py:class:`DataInterface` classes.

3. Getting metadata
-------------------

Now you have a :py:class:`ExampleNWBConverter` object that orchestrates the data interfaces. To get aggregated metadata
across all of your source files, call:

.. code-block:: python

    metadata = converter.get_metadata()

This will follow the default behavior of fetching metadata from the underlying :py:class:`DataInterface` instances one-by-one.
Any duplicate information will be overwritten by :py:class:`DataInterface` instances defined later in the
``data_interface_classes`` dictionary. You can define your own custom ``get_metadata`` method in the class definition
to override this behavior.

The metadata can then be manually modified with any additional user-input

.. code-block:: python

    metadata["NWBFile"].update(
        session_description="NeuroConv tutorial.",
        experimenter="My name",
    )
    metadata["Subject"].update(subject_id="M001", species="Mus musculus", age="P90D")

The final metadata dictionary should follow the form defined by ``converter.get_metadata_schema()``

4. Run conversion
-----------------

. Now run the entire conversion with

.. code-block:: python

    converter.run_conversion(metadata=metadata, nwbfile_path="my_nwbfile.nwb")

This method builds an `NWBFile` object with data and metadata from each of the ``DataInterface`` objects, and then
writes it to disk.

Though this example was only for two data streams (recording and spike-sorted data), it can easily extend to any
number of sources, including video of a subject, extracted position estimates, stimuli, or any other data source.

The sections below describe source schema and metadata schema in more detail through another example for two data
streams (ophys and ecephys data).