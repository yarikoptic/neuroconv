DataInterfaces
==============

Each :py:class:`DataInterface` is a class that converts a specific data format with NWB. There are many pre-built
DataInterface classes in the :ref:`conversion_gallery`. To use them, follow this workflow:
following workflow:

1. Find the appropriate DataInterface
-------------------------------------
:py:class:`DataInterface` classes include converters for extracellular electrophysiology, intracellular electrophysiology,
optical physiology, and behavior. The :ref:`conversion_gallery` shows each one with example code for how to use it.
If you do not see a :py:class:`DataInterface` for your data format, feel free to request it, or to built it yourself.

2. Initialization
------------------
Open the source files with

.. code-block:: python

    interface = ThisDataInterface(source_files)

This usually opens the underlying source files but does not read the data to memory.

3. Extract metadata
-------------------
Extract metadata with

.. code-block:: python

    metadata = interface.get_metadata()

This will pull metadata from the source files and organize it in a way that can be easily mapped to NWB. You can then
adjust or add metadata that could not be extracted from the source files.

.. code-block:: python

    metadata["Subject"] = dict(subject_id="001", species="Mus musculus", age="P90D")

.. note::
    To get the allowable form of metadata, run :meth:`interface.get_metadata_schema()`, which returns the a
    JSON-schema-like dictionary that defines of the required and optional fields.

4. Run conversion
-----------------
Once the metadata dictionary is assembled, you can pass it in to ``run_conversion``, which read the source data and
metadata and create an NWB file.

.. code-block:: python

    interface.run_conversion(nwbfile_path, metadata=metadata)

``run_conversion`` makes a number of assumptions in efficiently reading and writing source data, and in exactly where
the data should be saved within the NWB file. Many of these assumptions are changeable using the optional arguments
of the ``run_conversion`` method. It is worthwhile to review the docval of each :py:class:`DataInterface` you use to
see what these options are. Some keyword arguments common to many :py:class:`DataInterface` classes include:


stub_test: bool, optional (default False)
    If True, will truncate the data to run the conversion faster and take up less memory.

compression: str (optional, defaults to "gzip")
    Type of compression to use. Valid types are "gzip" and "lzf".
    Set to None to disable all compression.