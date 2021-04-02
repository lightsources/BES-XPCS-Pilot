#!/usr/bin/env python
import datetime
import h5py
import logging
import numpy as np
import warnings

logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)

A_KEV = 12.3984244  # voltage * wavelength product
# .nxs is known by PyMCA, .nx is not (use generic filter then)
NX_EXTENSION = ".nxs"
NX_APP_DEF_NAME = "NXxpcs"  # name of NeXus Application Definition


# TODO: not defined in NeXus at this time
# Need to create & propose this new Application Definition to NIAC


class NXCreator:
    """

    Write a NeXus file from the XPCS data

    These files contain several sets of results, including:

    * 1-D SAXS
    * 2-D SAXS
    * XPCS
    * and may include other analyses

    """

    def __init__(self, output_filename):
        self._output_filename = output_filename
        self.entry_group = None
        self.xpcs_group = None
        self.detector_group = None
        self.instrument_group = None

    def _init_group(self, h5parent, name, NX_class):
        """Common steps to initialize a NeXus HDF5 group."""
        group = h5parent.create_group(name)
        group.attrs["NX_class"] = NX_class
        print(group.name)
        return group

    def init_file(self):
        """Write the complete NeXus file."""
        #TODO check how this can be shared with other converters or moved to different module
        with h5py.File(self._output_filename, "w") as self.file:
            self.write_file_header(self.file)
            self.file.close()

    def write_file_header(self, output_file):
        """optional header metadata"""
        #TODO check how this can be implemented in a better way
        timestamp = datetime.datetime.now().isoformat(sep=" ", timespec="seconds")
        logger.debug("timestamp: %s", str(timestamp))
        # give the HDF5 root some more attributes
        output_file.attrs["file_name"] = output_file.filename
        output_file.attrs["file_time"] = timestamp
        #TODO does instrument name belong in header?
        output_file.attrs["instrument"] = "instrument_name"
        output_file.attrs["creator"] = __file__  # TODO: better choice?
        output_file.attrs["HDF5_Version"] = h5py.version.hdf5_version
        output_file.attrs["h5py_version"] = h5py.version.version

    def _create_dataset(self, group, name, value, **kwargs):
        """
        use this to create datasets in different (sub-)groups
        """
        if value is None:
            return
        ds = group.create_dataset(name, data=value)
        for k, v in kwargs.items():
            ds.attrs[k] = v
        ds.attrs["target"] = ds.name
        return ds

    def create_entry_group(self,
                           experiment_description: str = None,
                           title: str = None,
                           entry_number=None):
        """
        all information about the measurement
        see: https://manual.nexusformat.org/classes/base_classes/NXentry.html
        """

        if entry_number is None:
            entry_name = "entry"
        else:
            entry_name = f"entry_{entry_number}"

        with h5py.File(self._output_filename, "a") as file:
            entry_group = self._init_group(file, name=entry_name, NX_class="NXentry")
            self.entry_group_name = entry_group.name

            #TODO Decide on actual content of these entries
            entry_group.create_dataset("definition", data=NX_APP_DEF_NAME)
            if experiment_description is not None:
                experiment_description = experiment_description
            else:
                experiment_description = 'Default XPCS experiment'
            self._create_dataset(entry_group, "experiment_description", experiment_description)
            title = title if title is not None else "default"
            self._create_dataset(entry_group, "title", title)
            logger.debug("title: %s", title)

            # FIXME: Check NeXus structure: point to this group for default plot
            #file.attrs["default"] = self.entry_group.name.split("/")[-1]
            file.close()

    def create_xpcs_group(self,
                          g2: np.ndarray = None,
                          g2_unit: str = 'a.u',
                          g2_stderr: np.ndarray = None,
                          g2_partials_twotime: np.ndarray = None,
                          g2_twotime: np.ndarray = None,
                          twotime: np.ndarray = None,
                          tau: np.ndarray = None,
                          mask: np.ndarray = None,
                          dqmap: np.ndarray = None,
                          dqlist: np.ndarray = None,
                          dphilist: np.ndarray = None,
                          sqmap: np.ndarray = None,
                          *args,
                          **kwargs):

        # TODO check units and use pint to convert
        # https://pint.readthedocs.io/en/stable/

        """
        see Data Solutions Pilot Meeting Notes
        """

        signal_dataset = None
        # check   input data
        for i in locals():
            if i is None:
                # TODO check what happens if type hint is violated
                warnings.warn(f'Did not receive expected {i.__name__} data - '
                              f'Cannot write complete XPCS groups')
            # here we check the plottable data
            elif i in ("g2", "twotime", "tau"):
                signal_dataset = i
        with h5py.File(self._output_filename, "a") as file:
            self.xpcs_group = self._init_group(file[self.entry_group_name], "XPCS", "NXprocess")
            # TODO check if plottable data is assigned correctly
            if signal_dataset is None:
                warnings.warn(f'No plottable data available in {self.xpcs_group.__name__} cannot write signal attribute')
            else:
                # this defines the preferred plottable data
                self.xpcs_group.attrs["signal"] = signal_dataset

            # create datagroup and add datasets
            data_group = self._init_group(self.xpcs_group, "data", "NXdata")
            self._create_dataset(data_group, "g2", g2, units=g2_unit)
            self._create_dataset(data_group, "g2_stderr", g2_stderr, units=g2_unit)
            self._create_dataset(data_group, "tau", tau, units="au")

            # add twotime group and dataset
            twotime_group = self._init_group(self.xpcs_group, "twotime", "NXdata")
            self._create_dataset(twotime_group, "g2_partials_twotime", g2_partials_twotime, units="au")
            self._create_dataset(twotime_group, "g2_twotime", g2_twotime, units="au")
            # TODO find a better name for this entry: e.g. twotime_corr, twotime, C2T_all...?
            self._create_dataset(twotime_group, "twotime", twotime, units="au")

            # create instrument group and mask group, add datasets
            # TODO do we really want an instrument group here or direktly adding mask as a subentry?
            instrument_group = self._init_group(self.xpcs_group, "instrument", "NXdata")
            mask_group = self._init_group(instrument_group, "mask", "NXdata")
            self._create_dataset(mask_group, "mask", mask, units="au")
            self._create_dataset(mask_group, "dqmap", dqmap, units="au")
            self._create_dataset(mask_group, "dqlist", dqlist, units="au")
            self._create_dataset(mask_group, "dphilist", dphilist, units="au")
            self._create_dataset(mask_group, "sqmap", sqmap, units="au")
            file.close()

    def create_saxs_1d_group(self,
                             I: np.ndarray = None,
                             I_partial: np.ndarray = None,
                             *args,
                             **kwargs):
        """
        see Data Solutions Pilot Meeting Notes
        """

        for i in locals():
            if i is None:
                # TODO check what happens if type hint is violated
                warnings.warn(f'Did not received expected {i.__name__} data - '
                              f'Cannot write complete SAXS 1D group')
        with h5py.File(self._output_filename, "a") as file:
            saxs_1d_group = self._init_group(file[self.entry_group_name], "SAXS_1D", "NXprocess")
            data_group = self._init_group(saxs_1d_group, "data", "NXdata")
            self._create_dataset(data_group, "I", I, units="au")
            self._create_dataset(data_group, "I_partial", I_partial, units="au")
            file.close()


    def create_saxs_2d_group(self,
                             I: np.ndarray = None,
                             *args,
                             **kwargs):
        """
        see Data Solutions Pilot Meeting Notes
        """

        for i in locals():
            if i is None:
                # TODO check what happens if type hint is violated
                warnings.warn(f'Did not received expected {i.__name__} data - '
                              f'Cannot write complete SAXS 2D group')
        with h5py.File(self._output_filename, "a") as file:
            saxs_2d_group = self._init_group(file[self.entry_group_name], "SAXS_2D", "NXprocess")
            data_group = self._init_group(saxs_2d_group, "data", "NXdata")
            self._create_dataset(data_group, "I", I, units="au")
            file.close()

    def create_instrument_group(self,
                                count_time: np.ndarray = None,
                                frame_time: np.ndarray = None,
                                description: str = None,
                                distance: float = None,
                                x_pixel_size: float = None,
                                y_pixel_size: float = None,
                                energy: float = None
                                ):
        """Write the NXinstrument group."""
        with h5py.File(self._output_filename, "a") as file:
            self.instrument_group = self._init_group(file[self.entry_group_name], "instrument", "NXinstrument")

            # create detector group and add datasets
            detector_group = self._init_group(self.instrument_group, "detector", "NXdetector")
            self._create_dataset(detector_group, "count_time", count_time, units="au")
            self._create_dataset(detector_group, "frame_time", frame_time, units="au")
            self._create_dataset(detector_group, "description", description, units="au")
            self._create_dataset(detector_group, "distance", distance, units="au")
            self._create_dataset(detector_group, "x_pixel_size", x_pixel_size, units="au")
            self._create_dataset(detector_group, "y_pixel_size", y_pixel_size, units="au")

            # create monochromator group and add datasets
            mono_group = self._init_group(self.instrument_group, "monochromator", "NXmonochromator")
            self._create_dataset(mono_group, "energy", energy, units="au")
            file.close()

