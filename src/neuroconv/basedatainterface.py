"""Authors: Cody Baker and Ben Dichter."""
import uuid
from abc import abstractmethod, ABC
from typing import Optional

import numpy as np
from pynwb import NWBFile

from .utils import get_base_schema, get_schema_from_method_signature


class BaseDataInterface(ABC):
    """Abstract class defining the structure of all DataInterfaces."""

    @classmethod
    def get_source_schema(cls):
        """Infer the JSON schema for the source_data from the method signature (annotation typing)."""
        return get_schema_from_method_signature(cls.__init__, exclude=["source_data"])

    @classmethod
    def get_conversion_options_schema(cls):
        """Infer the JSON schema for the conversion options from the method signature (annotation typing)."""
        return get_schema_from_method_signature(cls.run_conversion, exclude=["nwbfile", "metadata"])

    def __init__(self, **source_data):
        self.source_data: dict = source_data

    def get_metadata_schema(self):
        """Retrieve JSON schema for metadata."""
        metadata_schema = get_base_schema(
            id_="metadata.schema.json",
            root=True,
            title="Metadata",
            description="Schema for the metadata",
            version="0.1.0",
        )
        return metadata_schema

    def get_metadata(self):
        """Child DataInterface classes should override this to match their metadata."""
        metadata = dict(
            NWBFile=dict(
                session_description="Auto-generated by neuroconv",
                identifier=str(uuid.uuid4()),
            ),
        )

        return metadata

    @abstractmethod
    def get_original_timestamps(self) -> np.ndarray:
        """
        Retrieve the original unaltered timestamps for the data in this interface.

        This function should retrieve the data on-demand by re-initializing the IO.

        Returns
        -------
        timestamps: numpy.ndarray
            The timestamps for the data stream.
        """
        raise NotImplementedError(
            "Unable to retrieve the original unaltered timestamps for this interface! "
            "Define the `get_original_timestamps` method for this interface."
        )

    @abstractmethod
    def get_timestamps(self) -> np.ndarray:
        """
        Retrieve the timestamps for the data in this interface.

        Returns
        -------
        timestamps: numpy.ndarray
            The timestamps for the data stream.
        """
        raise NotImplementedError(
            "Unable to retrieve timestamps for this interface! Define the `get_timestamps` method for this interface."
        )

    @abstractmethod
    def align_timestamps(self, aligned_timestamps: np.ndarray):
        """
        Replace all timestamps for this interface with those aligned to the common session start time.

        Must be in units seconds relative to the common 'session_start_time'.

        Parameters
        ----------
        aligned_timestamps : numpy.ndarray
            The synchronized timestamps for data in this interface.
        """
        raise NotImplementedError(
            "The protocol for synchronizing the timestamps of this interface has not been specified!"
        )

    def align_starting_time(self, starting_time: float):
        """
        Align the starting time for this interface relative to the common session start time.

        Must be in units seconds relative to the common 'session_start_time'.

        Parameters
        ----------
        starting_time : float
            The starting time for all temporal data in this interface.
        """
        self.align_timestamps(aligned_timestamps=self.get_timestamps() + starting_time)

    def align_by_interpolation(self, unaligned_timestamps: np.ndarray, aligned_timestamps: np.ndarray):
        """
        Interpolate the timestamps of this interface using a mapping from some unaligned time basis to its aligned one.

        Use this method if the unaligned timestamps of the data in this interface are not directly tracked by a primary
        system, but are known to occur between timestamps that are tracked, then align the timestamps of this interface
        by interpolating between the two.

        An example could be a metronomic TTL pulse (e.g., every second) from a secondary data stream to the primary
        timing system; if the time references of this interface are recorded within the relative time of the secondary
        data stream, then their exact time in the primary system is inferred given the pulse times.

        Must be in units seconds relative to the common 'session_start_time'.

        Parameters
        ----------
        unaligned_timestamps : numpy.ndarray
            The timestamps of the unaligned secondary time basis.
        aligned_timestamps : numpy.ndarray
            The timestamps aligned to the primary time basis.
        """
        self.align_timestamps(
            aligned_timestamps=np.interp(x=self.get_timestamps(), xp=unaligned_timestamps, fp=aligned_timestamps)
        )

    def get_conversion_options(self):
        """Child DataInterface classes should override this to match their conversion options."""
        return dict()

    @abstractmethod
    def run_conversion(
        self,
        nwbfile_path: Optional[str] = None,
        nwbfile: Optional[NWBFile] = None,
        metadata: Optional[dict] = None,
        overwrite: bool = False,
        **conversion_options,
    ):
        """
        Run the NWB conversion for the instantiated data interface.

        Parameters
        ----------
        nwbfile_path: FilePathType
            Path for where to write or load (if overwrite=False) the NWBFile.
            If specified, the context will always write to this location.
        nwbfile: NWBFile, optional
            An in-memory NWBFile object to write to the location.
        metadata: dict, optional
            Metadata dictionary with information used to create the NWBFile when one does not exist or overwrite=True.
        overwrite: bool, optional
            Whether or not to overwrite the NWBFile if one exists at the nwbfile_path.
            The default is False (append mode).
        verbose: bool, optional
            If 'nwbfile_path' is specified, informs user after a successful write operation.
            The default is True.
        """
        raise NotImplementedError("The run_conversion method for this DataInterface has not been defined!")
