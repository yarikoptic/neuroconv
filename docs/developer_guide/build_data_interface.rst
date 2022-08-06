Creating a DataInterface
========================
Creating a :py:class:`DataInterface` class is the best way to support a data standard that is not supported by the
existing :py:class:`DataInterface` classes.

Choosing a parent class
-----------------------
Your first step will be to determine what base class to use. All :py:class:`DataInterface` classes should be a
subclass of :py:class:`~neuroconv.basedatainterface.BaseDataInterface`, but there are several more specific
subclasses of this generic class that provide a framework for specific modalities and tooling. Choosing the right
parent for your new :py:class:`DataInterface` could save a lot of time in the end.

There are specific :py:class:`DataInterface` classes for each of the main modalities.

For extracellular electrophysiology, we leverage the `spikeinterface.extractors` module, which provides a common API
for many popular formats. :py:class:`DataInterface` classes targeting raw voltage traces should subclass the
:py:class:`~neuroconv.datainterfaces.ecephys.baserecordingextractor` to read from a :py:code:`Recording` class of
that format, and :py:class:`DataInterface` classes targeting the results of spike sorting should subclass the
:py:class:`~neuroconv.datainterfaces.ecephys.basesortingextractor` to read from a :py:code:`Sorting` class.

For intracellular electrophysiology, subclassing the :py:class:`~neuroconv.datainterfaces.icephys
.baseicephysinterface` will likely provide the best starting point.

For optical physiology, we have base classes built to interface with the ``roiextractors`` library, which provides a
common API for several popular imaging data formats. :py:class:`DataInterface` classes targeting raw imaging
data should subclass the :py:class:`~neuroconv.datainterfaces.ophys.baseimagingextractorinterface`, and
:py:class:`DataInterface` classes targeting cell segmentation should subclass the
:py:class:`~neuroconv.datainterfaces.ophys.basesegmentationextractorinterface`.

If these classes do not provide a convenient framework for your data source, there is no problem with subclassing the
:py:class:`~neuroconv.basedatainterface.BaseDataInterface` class directly.

Developing the DataInterface
----------------------------
Your :py:class:`DataInterface` class will need to implement the abstract methods declared in the
:py:class:`~neuroconv.basedatainterface.BaseDataInterface`: :code:`get_source_schema()`, :code:`get_metadata_schema()`,
:code:`get_metadata()`, and most importantly :code:`run_conversion()`. If you choose to subclass the
:py:class:`~neuroconv.basedatainterface.BaseDataInterface` class, you will need to implement these yourself.

Metadata
~~~~~~~~
It is a good idea to extract some relevant data from the standard, which can often be found in the data file header,
in an accompanying XML file, or in image metadata. The `session_start_time` can often be found in one of these
places, and is important to extract, since it is often not recorded anywhere else.

Run Conversion
~~~~~~~~~~~~~~
The trickiest part of building a `run_conversion` method is handling large datasets efficiently in memory. The
:py:class:`~hdmf.data_utils.GenericDataChunkIterator` provides a class that can control reading data piece-by-piece,
and writing it to HDF5 in a reasonable chunking and compression pattern. (`tutorial <https://hdmf.readthedocs.io/en/stable/tutorials/plot_generic_data_chunk_tutorial.html#sphx-glr-tutorials-plot-generic-data-chunk-tutorial-py>`_)


Contributing your DataInterface to NeuroConv
--------------------------------------------
You do not need to contribute your :py:class:`DataInterface` to NeuroConv. It can work perfectly well defined in a
lab-specific repository, and indeed many of the interfaces we develop are specific to one particular experiment
setup. If you do find yourself implementing a :py:class:`DataInterface` that would be broadly useful for others in
the community, Great! We would love to incorporate it. Contributing a new :py:class:`DataInterface` generally
requires these steps:

1. Open an issue on NeuroConv. Best practice is to open an issue on NeuroConv before you start developing a
   DataInterface that you plan to contribute. This will allow us to review the proposal and help suggest a best path
   forward, including what parent class to use, what metadata to extact, and how best to efficiently handle large data.

2. Implement the :py:class:`DataInterface`. The best way to propose a change to NeuroConv is to create a fork on your
   personal or organizational GitHub account and then to create a branch on that fork. This approach allows you to
   submit multiple pull requests simultaneously. Once you have a draft ready, `Create a Pull Request to NeuroConv
   <https://github.com/catalystneuro/neuroconv/pulls>`_. You can mark the pull request as work-in-progress by
   opening it in "draft mode." It is better to submit an imcomplete PR earlier rather than waiting until you finish.Our
   team will take a look at your class and may make some suggestions.

3. Contribute testing data. NeuroConv maintains libraries of testing data that hold small example files of each of
   our supported formats. These libraries are stored on GIN, and are split by modality:

   * behavior: https://gin.g-node.org/CatalystNeuro/behavior_testing_data
   * electrophysiology: https://gin.g-node.org/NeuralEnsemble/ephy_testing_data
   * optical physiology: https://gin.g-node.org/CatalystNeuro/ophys_testing_data

   These libraries use Git Annex to efficiently store these files. When you open a PR for your new
   :py:class:`DataInterface`, be ready to provide a small example file to our development team so we can help you add it
   to the appropriate data repository.

4. Write tests.

   Once the data is in the testing data repository, you can provide a read test that pulls this data and runs in through
   your :py:class:`DataInterface`. We aim to have tests for `run_conversion` and for `get_metadata` for all
   contributions of new :py:class:`DataInterface` classes.

5. Add a new page to the :ref:`Conversion Gallery <conversion_gallery>`. This page will be run as part of continuous
   integration, so it needs to run properly as written.

6. Mark changes in the CHANGELOG.md.
