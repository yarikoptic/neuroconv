"""Authors: Cody Baker, Heberto Mayorquin and Ben Dichter."""
from pathlib import Path
import json
from warnings import warn
from typing import Optional

from pynwb import NWBFile
from pynwb.ecephys import ElectricalSeries

from ..baserecordingextractorinterface import BaseRecordingExtractorInterface
from ....utils import get_schema_from_method_signature, get_schema_from_hdmf_class, FilePathType, dict_deep_update
from .spikeglx_utils import (
    get_session_start_time,
    _fetch_metadata_dic_for_spikextractors_spikelgx_object,
    _assert_single_shank_for_spike_extractors,
    fetch_stream_id_for_spikelgx_file,
)


def add_recording_extractor_properties(recording_extractor) -> None:
    """Automatically add shankgroup_name and shank_electrode_number for spikeglx."""

    probe = recording_extractor.get_probe()
    channel_ids = recording_extractor.get_channel_ids()

    if probe.get_shank_count() > 1:
        group_name = [contact_id.split("e")[0] for contact_id in probe.contact_ids]
        shank_electrode_number = [int(contact_id.split("e")[1]) for contact_id in probe.contact_ids]
    else:
        shank_electrode_number = recording_extractor.ids_to_indices(channel_ids)
        group_name = ["s0"] * len(channel_ids)

    recording_extractor.set_property(key="shank_electrode_number", ids=channel_ids, values=shank_electrode_number)
    recording_extractor.set_property(key="group_name", ids=channel_ids, values=group_name)

    contact_shapes = probe.contact_shapes  # The geometry of the contact shapes
    recording_extractor.set_property(key="contact_shapes", ids=channel_ids, values=contact_shapes)


class SpikeGLXRecordingInterface(BaseRecordingExtractorInterface):
    """Primary data interface class for converting the high-pass (ap) SpikeGLX format."""

    @classmethod
    def get_source_schema(cls) -> dict:
        source_schema = get_schema_from_method_signature(class_method=cls.__init__, exclude=["x_pitch", "y_pitch"])
        source_schema["properties"]["file_path"]["description"] = "Path to SpikeGLX file."
        return source_schema

    def __init__(
        self,
        file_path: FilePathType,
        stub_test: bool = False,
        spikeextractors_backend: bool = False,
        verbose: bool = True,
    ):
        """
        Parameters
        ----------
        file_path : FilePathType
            Path to .bin file. Point to .ap.bin for SpikeGLXRecordingInterface and .lf.bin for SpikeGLXLFPInterface.
        stub_test : bool, default: False
            Whether to shorten file for testing purposes.
        spikeextractors_backend : bool, default: False
            Whether to use the legacy spikeextractors library backend.
        verbose : bool, default: True
            Whether to output verbose text.
        """
        from probeinterface import read_spikeglx

        self.stub_test = stub_test
        self.stream_id = fetch_stream_id_for_spikelgx_file(file_path)

        if spikeextractors_backend:  # pragma: no cover
            # TODO: Remove spikeextractors backend
            warn(
                message=(
                    "Interfaces using a spikeextractors backend will soon be deprecated! "
                    "Please use the SpikeInterface backend instead."
                ),
                category=DeprecationWarning,
                stacklevel=2,
            )
            from spikeextractors import SpikeGLXRecordingExtractor
            from spikeinterface.core.old_api_utils import OldToNewRecording

            self.Extractor = SpikeGLXRecordingExtractor
            super().__init__(file_path=str(file_path), verbose=verbose)
            _assert_single_shank_for_spike_extractors(self.recording_extractor)
            self.meta = _fetch_metadata_dic_for_spikextractors_spikelgx_object(self.recording_extractor)
            self.recording_extractor = OldToNewRecording(oldapi_recording_extractor=self.recording_extractor)
        else:
            file_path = Path(file_path)
            folder_path = file_path.parent
            super().__init__(
                folder_path=folder_path,
                stream_id=self.stream_id,
                verbose=verbose,
            )
            self.source_data["file_path"] = str(file_path)
            self.meta = self.recording_extractor.neo_reader.signals_info_dict[(0, self.stream_id)]["meta"]

        # Mount the probe
        # TODO - this can be removed in the next release of SpikeInterface (probe mounts automatically)
        meta_filename = str(file_path).replace(".bin", ".meta").replace(".lf", ".ap")
        probe = read_spikeglx(meta_filename)
        self.recording_extractor.set_probe(probe, in_place=True)
        # Set electrodes properties
        add_recording_extractor_properties(self.recording_extractor)

    def get_metadata_schema(self) -> dict:
        metadata_schema = super().get_metadata_schema()
        metadata_schema["properties"]["Ecephys"]["properties"].update(
            ElectricalSeriesRaw=get_schema_from_hdmf_class(ElectricalSeries)
        )
        return metadata_schema

    def get_metadata(self) -> dict:
        metadata = super().get_metadata()
        session_start_time = get_session_start_time(self.meta)
        if session_start_time:
            metadata = dict_deep_update(metadata, dict(NWBFile=dict(session_start_time=session_start_time)))

        # Device metadata
        device = self.get_device_metadata()

        # Add groups metadata
        metadata["Ecephys"]["Device"] = [device]
        electrode_groups = [
            dict(
                name=group_name,
                description=f"a group representing shank {group_name}",
                location="unknown",
                device=device["name"],
            )
            for group_name in set(self.recording_extractor.get_property("group_name"))
        ]
        metadata["Ecephys"]["ElectrodeGroup"] = electrode_groups

        # Electrodes columns descriptions
        metadata["Ecephys"]["Electrodes"] = [
            dict(name="shank_electrode_number", description="0-indexed channel within a shank."),
            dict(name="group_name", description="Name of the ElectrodeGroup this electrode is a part of."),
            dict(name="contact_shapes", description="The shape of the electrode"),
        ]

        metadata["Ecephys"]["ElectricalSeriesRaw"] = dict(
            name="ElectricalSeriesRaw", description="Raw acquisition traces for the high-pass (ap) SpikeGLX data."
        )
        return metadata

    def get_device_metadata(self) -> dict:
        """Returns a device with description including the metadat as described here
        # https://billkarsh.github.io/SpikeGLX/Sgl_help/Metadata_30.html

        Returns
        -------
        dict
            a dict containing the metadata necessary for creating the device
        """

        meta = self.meta
        metadata_dict = dict()
        if "imDatPrb_type" in self.meta:
            probe_type_to_probe_description = {"0": "NP1.0", "21": "NP2.0(1-shank)", "24": "NP2.0(4-shank)"}
            probe_type = str(meta["imDatPrb_type"])
            probe_type_description = probe_type_to_probe_description[probe_type]
            metadata_dict.update(probe_type=probe_type, probe_type_description=probe_type_description)

        if "imDatFx_pn" in self.meta:
            metadata_dict.update(flex_part_number=meta["imDatFx_pn"])

        if "imDatBsc_pn" in self.meta:
            metadata_dict.update(connected_base_station_part_number=meta["imDatBsc_pn"])

        description_string = "no description"
        if metadata_dict:
            description_string = json.dumps(metadata_dict)
        device = dict(name="Neuropixel-Imec", description=description_string, manufacturer="Imec")

        return device

    def run_conversion(
        self,
        nwbfile_path: Optional[FilePathType] = None,
        nwbfile: Optional[NWBFile] = None,
        metadata: Optional[dict] = None,
        overwrite: bool = False,
        stub_test: bool = False,
        starting_time: Optional[float] = None,
        write_as: Optional[str] = "raw",
        write_electrical_series: bool = True,
        es_key: str = "ElectricalSeriesRaw",
        compression: Optional[str] = None,
        compression_opts: Optional[int] = None,
        iterator_type: str = "v2",
        iterator_opts: Optional[dict] = None,
    ):
        super().run_conversion(
            nwbfile_path=nwbfile_path,
            nwbfile=nwbfile,
            metadata=metadata,
            overwrite=overwrite,
            stub_test=stub_test,
            starting_time=starting_time,
            write_as=write_as,
            write_electrical_series=write_electrical_series,
            es_key=es_key,
            compression=compression,
            compression_opts=compression_opts,
            iterator_type=iterator_type,
            iterator_opts=iterator_opts,
        )


class SpikeGLXLFPInterface(SpikeGLXRecordingInterface):
    """Primary data interface class for converting the low-pass (lf) SpikeGLX format."""

    ExtractorName = "SpikeGLXRecordingExtractor"

    def get_metadata_schema(self) -> dict:
        metadata_schema = super().get_metadata_schema()

        del metadata_schema["properties"]["Ecephys"]["properties"]["ElectricalSeriesRaw"]
        metadata_schema["properties"]["Ecephys"]["properties"].update(
            ElectricalSeriesLFP=get_schema_from_hdmf_class(ElectricalSeries)
        )
        return metadata_schema

    def get_metadata(self) -> dict:
        metadata = super().get_metadata()
        del metadata["Ecephys"]["ElectricalSeriesRaw"]
        metadata["Ecephys"].update(
            ElectricalSeriesLFP=dict(
                name="ElectricalSeriesLFP", description="LFP traces for the processed (lf) SpikeGLX data."
            )
        )

        return metadata

    def run_conversion(
        self,
        nwbfile_path: Optional[FilePathType] = None,
        nwbfile: Optional[NWBFile] = None,
        metadata: Optional[dict] = None,
        overwrite: bool = False,
        stub_test: bool = False,
        starting_time: Optional[float] = None,
        write_as: Optional[str] = "raw",
        write_electrical_series: bool = True,
        es_key: str = "ElectricalSeriesLFP",
        compression: Optional[str] = None,
        compression_opts: Optional[int] = None,
        iterator_type: str = "v2",
        iterator_opts: Optional[dict] = None,
    ):
        super().run_conversion(
            nwbfile_path=nwbfile_path,
            nwbfile=nwbfile,
            metadata=metadata,
            overwrite=overwrite,
            stub_test=stub_test,
            starting_time=starting_time,
            write_as=write_as,
            write_electrical_series=write_electrical_series,
            es_key=es_key,
            compression=compression,
            compression_opts=compression_opts,
            iterator_type=iterator_type,
            iterator_opts=iterator_opts,
        )
