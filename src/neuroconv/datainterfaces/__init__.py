# Ecephys
from .ecephys.neuroscope.neuroscopedatainterface import (
    NeuroScopeRecordingInterface,
    NeuroScopeLFPInterface,
    NeuroScopeMultiRecordingTimeInterface,
    NeuroScopeSortingInterface,
)
from .ecephys.spikeglx.spikeglxdatainterface import SpikeGLXRecordingInterface, SpikeGLXLFPInterface
from .ecephys.spikeglx.spikeglxnidqinterface import SpikeGLXNIDQInterface
from .ecephys.spikegadgets.spikegadgetsdatainterface import SpikeGadgetsRecordingInterface
from .ecephys.spikeinterface.sipickledatainterfaces import (
    SIPickleRecordingInterface,
    SIPickleSortingInterface,
)
from .ecephys.intan.intandatainterface import IntanRecordingInterface
from .ecephys.ced.ceddatainterface import CEDRecordingInterface
from .ecephys.cellexplorer.cellexplorerdatainterface import CellExplorerSortingInterface
from .ecephys.blackrock.blackrockdatainterface import (
    BlackrockRecordingInterface,
    BlackrockSortingInterface,
)
from .ecephys.openephys.openephysdatainterface import OpenEphysRecordingInterface
from .ecephys.openephys.openephysbinarydatainterface import OpenEphysSortingInterface
from .ecephys.axona.axonadatainterface import (
    AxonaRecordingInterface,
    AxonaPositionDataInterface,
    AxonaLFPDataInterface,
    AxonaUnitRecordingInterface,
)
from .ecephys.neuralynx.neuralynxdatainterface import NeuralynxRecordingInterface, NeuralynxSortingInterface
from .ecephys.phy.phydatainterface import PhySortingInterface
from .ecephys.kilosort.kilosortdatainterface import KiloSortSortingInterface
from .ecephys.edf.edfdatainterface import EDFRecordingInterface
from .ecephys.tdt.tdtdatainterface import TdtRecordingInterface
from .ecephys.plexon.plexondatainterface import PlexonRecordingInterface, PlexonSortingInterface
from .ecephys.biocam.biocamdatainterface import BiocamRecordingInterface
from .ecephys.alphaomega.alphaomegadatainterface import AlphaOmegaRecordingInterface
from .ecephys.mearec.mearecdatainterface import MEArecRecordingInterface
from .ecephys.mcsraw.mcsrawdatainterface import MCSRawRecordingInterface

# Icephys
from .icephys.abf.abfdatainterface import AbfInterface


# Ophys
from .ophys.caiman.caimandatainterface import CaimanSegmentationInterface
from .ophys.cnmfe.cnmfedatainterface import CnmfeSegmentationInterface
from .ophys.suite2p.suite2pdatainterface import Suite2pSegmentationInterface
from .ophys.extract.extractdatainterface import ExtractSegmentationInterface
from .ophys.sima.simadatainterface import SimaSegmentationInterface

from .ophys.sbx.sbxdatainterface import SbxImagingInterface
from .ophys.tiff.tiffdatainterface import TiffImagingInterface
from .ophys.hdf5.hdf5datainterface import Hdf5ImagingInterface
from .ophys.scanimage.scanimageimaginginterface import ScanImageImagingInterface


# Behavior
from .behavior.video.videodatainterface import VideoInterface, MovieInterface
from .behavior.deeplabcut.deeplabcutdatainterface import DeepLabCutInterface
from .behavior.sleap.sleapdatainterface import SLEAPInterface

# Text
from .text.csv.csvtimeintertervalsinterface import CsvTimeIntervalsInterface
from .text.excel.exceltimeintervalsinterface import ExcelTimeIntervalsInterface

interface_list = [
    # Ecephys
    NeuralynxRecordingInterface,
    NeuralynxSortingInterface,
    NeuroScopeRecordingInterface,
    NeuroScopeMultiRecordingTimeInterface,
    NeuroScopeSortingInterface,
    NeuroScopeLFPInterface,
    SpikeGLXRecordingInterface,
    SpikeGLXLFPInterface,
    SpikeGLXNIDQInterface,
    SpikeGadgetsRecordingInterface,
    SIPickleRecordingInterface,
    SIPickleSortingInterface,
    IntanRecordingInterface,
    CEDRecordingInterface,
    CellExplorerSortingInterface,
    BlackrockRecordingInterface,
    BlackrockSortingInterface,
    OpenEphysRecordingInterface,
    OpenEphysSortingInterface,
    PhySortingInterface,
    KiloSortSortingInterface,
    AxonaRecordingInterface,
    AxonaPositionDataInterface,
    AxonaLFPDataInterface,
    AxonaUnitRecordingInterface,
    EDFRecordingInterface,
    TdtRecordingInterface,
    PlexonRecordingInterface,
    PlexonSortingInterface,
    BiocamRecordingInterface,
    AlphaOmegaRecordingInterface,
    MEArecRecordingInterface,
    MCSRawRecordingInterface,
    # Icephys
    AbfInterface,
    # Ophys
    CaimanSegmentationInterface,
    CnmfeSegmentationInterface,
    Suite2pSegmentationInterface,
    ExtractSegmentationInterface,
    SimaSegmentationInterface,
    SbxImagingInterface,
    TiffImagingInterface,
    Hdf5ImagingInterface,
    ScanImageImagingInterface,
    # Behavior
    MovieInterface,  # TO-DO: deprecate on April 2023
    VideoInterface,
    DeepLabCutInterface,
    SLEAPInterface,
    # Text
    CsvTimeIntervalsInterface,
    ExcelTimeIntervalsInterface,
]
