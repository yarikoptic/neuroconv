"""Authors: Heberto Mayorquin, Cody Baker and Ben Dichter."""
from typing import Optional

import numpy as np
from pynwb import NWBFile
from pynwb.device import Device
from pynwb.ophys import Fluorescence, ImageSegmentation, ImagingPlane, TwoPhotonSeries

from ...baseextractorinterface import BaseExtractorInterface
from ...utils import get_schema_from_hdmf_class, fill_defaults, FilePathType, get_base_schema


class BaseSegmentationExtractorInterface(BaseExtractorInterface):
    """Parent class for all SegmentationExtractorInterfaces."""

    ExtractorModuleName: Optional[str] = "roiextractors"

    def __init__(self, **source_data):
        super().__init__(**source_data)
        self.segmentation_extractor = self.Extractor(**source_data)

    def get_metadata_schema(self) -> dict:
        metadata_schema = super().get_metadata_schema()
        metadata_schema["required"] = ["Ophys"]
        metadata_schema["properties"]["Ophys"] = get_base_schema()
        metadata_schema["properties"]["Ophys"]["properties"] = dict(
            Device=dict(type="array", minItems=1, items=get_schema_from_hdmf_class(Device)),
        )
        metadata_schema["properties"]["Ophys"]["properties"].update(
            Fluorescence=get_schema_from_hdmf_class(Fluorescence),
            ImageSegmentation=get_schema_from_hdmf_class(ImageSegmentation),
            ImagingPlane=get_schema_from_hdmf_class(ImagingPlane),
            TwoPhotonSeries=get_schema_from_hdmf_class(TwoPhotonSeries),
        )
        metadata_schema["properties"]["Ophys"]["required"] = ["Device", "ImageSegmentation"]

        # Temporary fixes until centralized definition of metadata schemas
        metadata_schema["properties"]["Ophys"]["properties"]["ImagingPlane"].update(type="array")
        metadata_schema["properties"]["Ophys"]["properties"]["TwoPhotonSeries"].update(type="array")

        metadata_schema["properties"]["Ophys"]["properties"]["Fluorescence"]["properties"]["roi_response_series"][
            "items"
        ]["required"] = list()
        metadata_schema["properties"]["Ophys"]["properties"]["ImageSegmentation"]["additionalProperties"] = True
        metadata_schema["properties"]["Ophys"]["properties"]["Fluorescence"]["properties"]["roi_response_series"].pop(
            "maxItems"
        )
        metadata_schema["properties"]["Ophys"]["properties"]["DfOverF"] = metadata_schema["properties"]["Ophys"][
            "properties"
        ]["Fluorescence"]

        fill_defaults(metadata_schema, self.get_metadata())
        return metadata_schema

    def get_metadata(self) -> dict:
        from ...tools.roiextractors import get_nwb_segmentation_metadata

        metadata = super().get_metadata()
        metadata.update(get_nwb_segmentation_metadata(self.segmentation_extractor))
        return metadata

    def get_original_timestamps(self) -> np.ndarray:
        raise NotImplementedError(
            "Unable to retrieve the original unaltered timestamps for this interface! "
            "Define the `get_original_timestamps` method for this interface."
        )

    def get_timestamps(self) -> np.ndarray:
        raise NotImplementedError(
            "Unable to retrieve timestamps for this interface! Define the `get_timestamps` method for this interface."
        )

    def align_timestamps(self, aligned_timestamps: np.ndarray):
        raise NotImplementedError(
            "The protocol for synchronizing the timestamps of this interface has not been specified!"
        )

    def run_conversion(
        self,
        nwbfile_path: Optional[FilePathType] = None,
        nwbfile: Optional[NWBFile] = None,
        metadata: Optional[dict] = None,
        overwrite: bool = False,
        stub_test: bool = False,
        stub_frames: int = 100,
        include_roi_centroids: bool = True,
        include_roi_acceptance: bool = True,
        mask_type: Optional[str] = "image",  # Optional[Literal["image", "pixel", "voxel"]]
        iterator_options: Optional[dict] = None,
        compression_options: Optional[dict] = None,
    ):
        """

        Parameters
        ----------
        nwbfile_path : FilePathType, optional
        nwbfile : NWBFile, optional
            The NWBFile to add the plane segmentation to.
        metadata : dict, optional
            The metadata for the interface
        overwrite : bool, default: False
        stub_test : bool, default: False
        stub_frames : int, default: 100
        include_roi_centroids : bool, default: True
            Whether to include the ROI centroids on the PlaneSegmentation table.
            If there are a very large number of ROIs (such as in whole-brain recordings),
            you may wish to disable this for faster write speeds.
        include_roi_acceptance : bool, default: True
            Whether to include if the detected ROI was 'accepted' or 'rejected'.
            If there are a very large number of ROIs (such as in whole-brain recordings), you may wish to ddisable this for
            faster write speeds.
        mask_type : {'image', 'pixel', 'voxel'}, optional
            There are two types of ROI masks in NWB: ImageMasks and PixelMasks.
            Image masks have the same shape as the reference images the segmentation was applied to, and weight each pixel
                by its contribution to the ROI (typically boolean, with 0 meaning 'not in the ROI').
            Pixel masks are instead indexed by ROI, with the data at each index being the shape of the image by the number
                of pixels in each ROI.
            Voxel masks are instead indexed by ROI, with the data at each index being the shape of the volume by the number
                of voxels in each ROI.
            Specify your choice between these three as mask_type='image', 'pixel', 'voxel', or None.
            If None, the mask information is not written to the NWB file.
            Defaults to 'image'.
        iterator_options : dict, optional
            The options to use when iterating over the image masks of the segmentation extractor.
        compression_options : dict, optional
            The options to use when compressing the image masks of the segmentation extractor.

        Returns
        -------

        """
        from ...tools.roiextractors import write_segmentation

        if stub_test:
            stub_frames = min([stub_frames, self.segmentation_extractor.get_num_frames()])
            segmentation_extractor = self.segmentation_extractor.frame_slice(start_frame=0, end_frame=stub_frames)
        else:
            segmentation_extractor = self.segmentation_extractor

        write_segmentation(
            segmentation_extractor=segmentation_extractor,
            nwbfile_path=nwbfile_path,
            nwbfile=nwbfile,
            metadata=metadata,
            overwrite=overwrite,
            verbose=self.verbose,
            include_roi_centroids=include_roi_centroids,
            include_roi_acceptance=include_roi_acceptance,
            mask_type=mask_type,
            iterator_options=iterator_options,
            compression_options=compression_options,
        )
