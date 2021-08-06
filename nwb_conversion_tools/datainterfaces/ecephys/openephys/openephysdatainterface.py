"""Authors: Luiz Tauffer"""
import random
import string
import pytz
import uuid
from typing import Union, Optional
from pathlib import Path
import spikeextractors as se
from pynwb import NWBFile

from ..baserecordingextractorinterface import BaseRecordingExtractorInterface
from ..basesortingextractorinterface import BaseSortingExtractorInterface
from ....utils.json_schema import get_schema_from_method_signature

PathType = Union[str, Path, None]


class OpenEphysRecordingExtractorInterface(BaseRecordingExtractorInterface):
    """Primary data interface class for converting a OpenEphysRecordingExtractor."""

    RX = se.OpenEphysRecordingExtractor

    @classmethod
    def get_source_schema(cls):
        """Compile input schema for the RecordingExtractor."""
        source_schema = get_schema_from_method_signature(
            class_method=cls.__init__, exclude=["recording_id", "experiment_id", "stub_test"]
        )
        source_schema["properties"]["folder_path"]["format"] = "directory"
        source_schema["properties"]["folder_path"]["description"] = "Path to directory containing OpenEphys files."
        return source_schema

    def __init__(
        self,
        folder_path: PathType,
        experiment_id: Optional[int] = 0,
        recording_id: Optional[int] = 0,
        stub_test: Optional[bool] = False,
    ):
        super().__init__(folder_path=str(folder_path), experiment_id=experiment_id, recording_id=recording_id)
        if stub_test:
            self.subset_channels = [0, 1]

    def get_metadata(self):
        """Auto-fill as much of the metadata as possible. Must comply with metadata schema."""
        metadata = super().get_metadata()

        # Open file and extract info
        session_start_time = self.recording_extractor._fileobj.experiments[0].datetime
        session_start_time_tzaware = pytz.timezone("EST").localize(session_start_time)

<<<<<<< HEAD
        for channel_id in self.recording_extractor.get_channel_ids():
            self.recording_extractor.set_channel_property(
                channel_id=channel_id,
                property_name="group_name",
                value="ElectrodeGroup"
            )

        metadata['NWBFile'] = dict(
            session_start_time=session_start_time_tzaware.strftime('%Y-%m-%dT%H:%M:%S'),
=======
        metadata["NWBFile"] = dict(
            session_start_time=session_start_time_tzaware.strftime("%Y-%m-%dT%H:%M:%S"),
>>>>>>> master
        )
        return metadata


class OpenEphysSortingExtractorInterface(BaseSortingExtractorInterface):
    """Primary data interface class for converting OpenEphys spiking data."""

    SX = se.OpenEphysSortingExtractor

    @classmethod
    def get_source_schema(cls):
        """Compile input schema for the SortingExtractor."""
        metadata_schema = get_schema_from_method_signature(
            class_method=cls.__init__, exclude=["recording_id", "experiment_id"]
        )
        metadata_schema["properties"]["folder_path"]["format"] = "directory"
        metadata_schema["properties"]["folder_path"]["description"] = "Path to directory containing OpenEphys files."
        metadata_schema["additionalProperties"] = False
        return metadata_schema

    def __init__(self, folder_path: PathType, experiment_id: Optional[int] = 0, recording_id: Optional[int] = 0):
        super().__init__(folder_path=str(folder_path), experiment_id=experiment_id, recording_id=recording_id)
