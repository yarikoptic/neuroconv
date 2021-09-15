"""Authors: Cody Baker and Ben Dichter."""
from pathlib import Path
import numpy as np
from typing import Optional
from tqdm import tqdm
from warnings import warn

import psutil
from pynwb import NWBFile
from pynwb.image import ImageSeries
from hdmf.backends.hdf5.h5_utils import H5DataIO
from hdmf.data_utils import DataChunkIterator

from ....basedatainterface import BaseDataInterface
from ....utils.conversion_tools import check_regular_timestamps, get_module
from ....utils.json_schema import get_schema_from_method_signature, FilePathType
from .movie_utils import get_movie_timestamps, get_movie_fps, get_frame_shape


try:
    import cv2

    HAVE_OPENCV = True
except ImportError:
    HAVE_OPENCV = False
INSTALL_MESSAGE = "Please install opencv to use this extractor (pip install opencv-python)!"


class MovieInterface(BaseDataInterface):
    """Data interface for writing movies as ImageSeries."""

    def __init__(self, file_path: FilePathType):
        """
        Create the interface for writing movies as ImageSeries.

        Parameters
        ----------
        file_paths : list of FilePathTypes
            Many movie storage formats segment a sequence of movies over the course of the experiment.
            Pass the file paths for this movies as a list in sorted, consecutive order.
        """
        assert HAVE_OPENCV, INSTALL_MESSAGE
        super().__init__(file_path=file_path)

    @classmethod
    def get_source_schema(cls):
        return get_schema_from_method_signature(cls.__init__)

    def run_conversion(
        self,
        nwbfile: NWBFile,
        metadata: dict,
        stub_test: bool = False,
        external_mode: bool = True,
        starting_time: Optional[float] = None,
        chunk_data: bool = True,
        module_name: Optional[str] = None,
        module_description: Optional[str] = None,
    ):
        """
        Convert the movie data files to ImageSeries and write them in the NWBFile.

        Parameters
        ----------
        nwbfile : NWBFile
        metadata : dict
        stub_test : bool, optional
            If True, truncates the write operation for fast testing. The default is False.
        external_mode : bool, optional
            ImageSeries in NWBFiles may contain either explicit movie data or file paths to external movie files. If
            True, this utilizes the more efficient method of merely encoding the file path linkage (recommended). For
            data sharing, the video files must be contained in the same folder as the NWBFile. If the intention of this
            NWBFile involves an upload to DANDI, the non-NWBFile types are not allowed so this flag would have to be
            set to False. The default is True.
        starting_time : list, optional
            List of start times for each movie. If unspecified, assumes that the movies in the file_paths list are in
            sequential order and are contiguous.
        chunk_data : bool, optional
            If True, uses a DataChunkIterator to read and write the movie, reducing overhead RAM usage at the cost of
            reduced conversion speed (compared to loading video entirely into RAM as an array). This will also force to
            True, even if manually set to False, whenever the video file size exceeds available system RAM by a factor
            of 70 (from compression experiments). Based on experiements for a ~30 FPS system of ~400 x ~600 color
            frames, the equivalent uncompressed RAM usage is around 2GB per minute of video. The default is True.
        module_name: str, optional
            Name of the processing module to add the ImageSeries object to. Default behavior is to add as acquisition.
        module_description: str, optional
            If the processing module specified by module_name does not exist, it will be created with this description.
            The default description is the same as used by the conversion_tools.get_module function.
        """
        file_path = self.source_data["file_path"]

        if stub_test:
            count_max = 10
        else:
            count_max = np.inf
        if starting_time is None:
            starting_time = 0.0

        timestamps = starting_time + get_movie_timestamps(movie_file=file_path)
        nwb_module = "acquisition" if module_name is None else module_name

        image_series_kwargs = dict(
            name=f"Video: {Path(file_path).stem}", description="Video recorded by camera.", unit="Frames"
        )
        if nwb_module in metadata and "ImageSeries" in metadata[nwb_module]:
            image_series_kwargs.update(metadata[nwb_module]["ImageSeries"])

        if check_regular_timestamps(ts=timestamps):
            fps = get_movie_fps(movie_file=file_path)
            image_series_kwargs.update(starting_time=starting_time, rate=fps)
        else:
            image_series_kwargs.update(timestamps=H5DataIO(timestamps, compression="gzip"))

        if external_mode:
            image_series_kwargs.update(format="external", external_file=[file_path])
        else:
            uncompressed_estimate = Path(file_path).stat().st_size * 70
            available_memory = psutil.virtual_memory().available
            if not chunk_data and uncompressed_estimate >= available_memory:
                warn(
                    f"Not enough memory (estimated {round(uncompressed_estimate/1e9, 2)} GB) to load movie file as "
                    f"array ({round(available_memory/1e9, 2)} GB available)! Forcing chunk_data to True."
                )
                chunk_data = True

            total_frames = len(timestamps)
            frame_shape = get_frame_shape(movie_file=file_path)
            maxshape = [total_frames]
            maxshape.extend(frame_shape)
            best_gzip_chunk = (1, frame_shape[0], frame_shape[1], 3)
            tqdm_pos, tqdm_mininterval = (0, 10)
            if chunk_data:

                def data_generator(file, count_max):
                    cap = cv2.VideoCapture(str(file))
                    for _ in range(min(count_max, total_frames)):
                        success, frame = cap.read()
                        yield frame
                    cap.release()

                mov = DataChunkIterator(
                    data=tqdm(
                        iterable=data_generator(file=file_path, count_max=count_max),
                        desc=f"Copying movie data for {Path(file_path).name}",
                        position=tqdm_pos,
                        total=total_frames,
                        mininterval=tqdm_mininterval,
                    ),
                    iter_axis=0,  # nwb standard is time as zero axis
                    maxshape=tuple(maxshape),
                )
                image_series_kwargs.update(data=H5DataIO(mov, compression="gzip", chunks=best_gzip_chunk))
            else:
                cap = cv2.VideoCapture(str(file_path))
                mov = []
                with tqdm(
                    desc=f"Reading movie data for {Path(file_path).name}",
                    position=tqdm_pos,
                    total=total_frames,
                    mininterval=tqdm_mininterval,
                ) as pbar:
                    for _ in range(min(count_max, total_frames)):
                        success, frame = cap.read()
                        mov.append(frame)
                        pbar.update(1)
                cap.release()
                image_series_kwargs.update(
                    data=H5DataIO(
                        DataChunkIterator(
                            tqdm(
                                iterable=np.array(mov),
                                desc=f"Writing movie data for {Path(file_path).name}",
                                position=tqdm_pos,
                                mininterval=tqdm_mininterval,
                            ),
                            iter_axis=0,  # nwb standard is time as zero axis
                            maxshape=tuple(maxshape),
                        ),
                        compression="gzip",
                        chunks=best_gzip_chunk,
                    )
                )
        if module_name is None:
            nwbfile.add_acquisition(ImageSeries(**image_series_kwargs))
        else:
            get_module(nwbfile=nwbfile, name=module_name, description=module_description).add(
                ImageSeries(**image_series_kwargs)
            )
