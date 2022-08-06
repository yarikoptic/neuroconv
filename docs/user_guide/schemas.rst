Schemas
=======

As NeuroConv supports more and more data formats, the corresponding :py:class:`DataInterface` classes are increasingly
numerous and diverse. Different :py:class:`DataInterface` classes require different input fields, and have different
rules for what is required and what is optional. The complexity is increased by :py:class:`NWBConverter` classes, which
combine these rules across multiple :py:class:`DataInterface` classes. As a class user, you need clearly defined rules
about the allowable form of the dictionaries that are input as ``source_data``, ``metadata``, and
``conversion_options``. In each of
these cases, NeuroConv uses JSON-schema-like dictionaries to provide guidance for the forms of these inputs. For any
:py:class:`DataInterface` or any :py:class:`NWBConverter` object, you can call ``get_source_schema``,
``get_metadata_schema``,
``get_conversion_options_schema``, which will describe the allowable form of the hierarchical dictionary for that
argument and indicate which fields are required.

.. _source_schema:

Source Schema
-------------

The source schema is a JSON schema that defines the rules for organizing the source data. :py:class:`DataInterface`
classes have the class method ``get_source_schema``, which returns the source schema in form of a dictionary.

For example,
:py:class:`~neuroconv.datainterfaces.ecephys.blackrock.blackrockdatainterface.BlackrockRecordingExtractorInterface`
has the following source schema:

.. code-block:: python

    BlackrockRecordingExtractorInterface.get_source_schema()

.. code-block:: json

    {
      "required": ["file_path"],
      "properties": {
        "file_path": {
          "format": "file",
          "type": "string",
          "description": "Path to Blackrock file."
        },
        "nsx_override": {
          "type": "string"
        },
        "verbose": {
          "type": "boolean",
          "default": true
        },
        "spikeextractors_backend": {
          "type": "boolean",
          "default": false
        }
      },
      "type": "object",
      "additionalProperties": false
    }

and the source schema for
:py:class:`~neuroconv.datainterfaces.ecephys.phy.phydatainterface.PhySortingInterface` is:

.. code-block:: python

    PhySortingInterface.get_source_schema()

.. code-block:: json

    {
      "required": [
        "folder_path"
      ],
      "properties": {
        "folder_path": {
          "format": "directory",
          "type": "string"
        },
        "exclude_cluster_groups": {
          "type": "array"
        },
        "verbose": {
          "type": "boolean",
          "default": true
        },
        "spikeextractors_backend": {
          "type": "boolean",
          "default": false
        }
      },
      "type": "object",
      "additionalProperties": false
    }

So far, this is not that informative, as it is simply a different way of communicating the call signature of the
``__init__`` of each class. These schemas become useful when we combine them. Let's take a look at the source schema
of the custom NWBConverter defined in the previous section:

.. code-block:: python

    ExampleNWBConverter.get_source_schema()

.. code-block:: json

    {
      "required": [],
      "properties": {
        "BlackrockRecording": {
          "required": [
            "file_path"
          ],
          "properties": {
            "file_path": {
              "format": "file",
              "type": "string",
              "description": "Path to Blackrock file."
            },
            "nsx_override": {
              "type": "string"
            },
            "verbose": {
              "type": "boolean",
              "default": true
            },
            "spikeextractors_backend": {
              "type": "boolean",
              "default": false
            }
          },
          "type": "object",
          "additionalProperties": false
        },
        "PhySorting": {
          "required": [
            "folder_path"
          ],
          "properties": {
            "folder_path": {
              "format": "directory",
              "type": "string"
            },
            "exclude_cluster_groups": {
              "type": "array"
            },
            "verbose": {
              "type": "boolean",
              "default": true
            },
            "spikeextractors_backend": {
              "type": "boolean",
              "default": false
            }
          },
          "type": "object",
          "additionalProperties": false
        }
      },
      "type": "object",
      "additionalProperties": false,
      "$schema": "http://json-schema.org/draft-07/schema#",
      "$id": "source.schema.json",
      "title": "Source data schema",
      "description": "Schema for the source data, files and directories",
      "version": "0.1.0"
    }

.. _metadata_schema:

Metadata Schemas
----------------
Similarly to the source schema, the metadata schema are defined for each :py:class:`DataInterface` with the method
``get_metadata_schema()``. Calling ``get_metadata_schema()`` on an :py:class:`NWBConverter` will aggregate the
results of the :py:class:`DataInterface` objects within. However, note that the results are combined here differently
from how they were with the source schema. With the source schema, the input paths were separated out by
DataInterface label, but with metadata the results are combined into a single structure:







The metadata schema is a JSON schema that defines the rules for organizing the metadata. The metadata properties map
to the NWB classes necessary for any specific conversion task. Similar to input data, each ``DataInterface`` produces
its own metadata schema reflecting the specificities of the dataset it interfaces with. The ``DataInterface``
specific metadata schema can be obtained via method ``get_metadata_schema()``. For example, the
``EcephysDataInterface`` could return a metadata schema similar to this:

.. code-block:: json

    {
      "$schema": "http://json-schema.org/draft-07/schema#",
      "$id": "metafile.schema.json",
      "title": "Metadata",
      "description": "Schema for the metadata",
      "version": "0.1.0",
      "type": "object",
      "required": ["NWBFile"],
      "additionalProperties": false,
      "properties": {
        "NWBFile": {
          "type": "object",
          "additionalProperties": false,
          "tag": "pynwb.file.NWBFile",
          "required": ["session_description", "identifier", "session_start_time"],
          "properties": {
            "session_description": {
              "type": "string",
              "format": "long",
              "description": "a description of the session where this data was generated"
            },
            "identifier": {
              "type": "string",
              "description": "a unique text identifier for the file"
            },
            "session_start_time": {
              "type": "string",
              "description": "the start date and time of the recording session",
              "format": "date-time"
            }
          }
        },
        "Ecephys": {
          "type": "object",
          "title": "Ecephys",
          "required": [],
          "properties": {
            "Device": {"$ref": "#/definitions/Device"},
            "ElectricalSeries_raw": {"$ref": "#/definitions/ElectricalSeries"},
            "ElectricalSeries_processed": {"$ref": "#/definitions/ElectricalSeries"},
            "ElectrodeGroup": {"$ref": "#/definitions/ElectrodeGroup"}
          }
        }
      }
    }

Each DataInterface also provides a way to automatically fetch as much metadata as possible
directly from the dataset it interfaces with. This is done with the method ``get_metadata()``.

``OphysDataInterface`` would return a similar dictionaries for metadata_schema and metadata,
with properties related to optophysiology data. The ``LabConverter`` will combine the
DataInterfaces specific schemas and metadatas into a full dictionaries, and potentially
include properties that lie outside the scope of specific DataInterfaces.
