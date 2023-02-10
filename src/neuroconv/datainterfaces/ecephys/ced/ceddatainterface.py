"""Authors: Heberto Mayorquin, Luiz Tauffer."""
from pathlib import Path

from ..baserecordingextractorinterface import BaseRecordingExtractorInterface
from ....tools import get_package
from ....utils import get_schema_from_method_signature, FilePathType


def _test_sonpy_installation() -> None:
    get_package(
        package_name="sonpy",
        excluded_python_versions=["3.10", "3.11"],
        excluded_platforms_and_python_versions=dict(darwin=["3.7"]),
    )


class CEDRecordingInterface(BaseRecordingExtractorInterface):
    """Primary data interface class for converting data from CED (Cambridge Electronic
    Design) using the :py:class:`~spikeinterface.extractors.CedRecordingExtractor`."""

    ExtractorName = "CedRecordingExtractor"

    @classmethod
    def get_source_schema(cls):
        source_schema = get_schema_from_method_signature(class_method=cls.__init__, exclude=["smrx_channel_ids"])
        source_schema.update(additionalProperties=True)
        source_schema["properties"]["file_path"].update(description="Path to CED data file.")
        return source_schema

    @classmethod
    def get_all_channels_info(cls, file_path: FilePathType):
        """Retrieve and inspect necessary channel information prior to initialization."""
        _test_sonpy_installation()
        getattr(cls, "RX")  # Required to trigger dynamic access in case this method is called first
        return cls.RX.get_all_channels_info(file_path=file_path)

    def __init__(self, file_path: FilePathType, verbose: bool = True):
        """
        Initialize reading of CED file.

        Parameters
        ----------
        file_path: FilePathType
            Path to .smr or .smrx file.
        verbose: bool, default: True
        """
        _test_sonpy_installation()

        stream_id = "1" if Path(file_path).suffix == ".smr" else None
        super().__init__(file_path=file_path, stream_id=stream_id, verbose=verbose)

        # Subset raw channel properties
        signal_channels = self.recording_extractor.neo_reader.header["signal_channels"]
        channel_ids_of_raw_data = [channel_info[1] for channel_info in signal_channels if channel_info[4] == "mV"]
        self.recording_extractor = self.recording_extractor.channel_slice(channel_ids=channel_ids_of_raw_data)
