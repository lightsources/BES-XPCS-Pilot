#!/usr/bin/env python
import logging
import warnings
import numpy as np

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

    def __init__(self, h5root):
        self._h5root = h5root

    def _init_group(self, h5parent, nm, NX_class):
        """Common steps to initialize a NeXus HDF5 group."""
        group = h5parent.create_group(nm)
        group.attrs["NX_class"] = NX_class
        return group

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
                           experiment_description: str=None,
                           title: str=None,
                           count_entry=None):
        """
        all information about the measurement
        see: https://manual.nexusformat.org/classes/base_classes/NXentry.html
        """

        if count_entry is None:
            entry_name = "entry"
        else:
            #TODO how will count_entry be defined when connecting to the loader?
            entry_name = f"entry_{count_entry}"
        group = self._init_group(self._h5root, nm=entry_name, NX_class="NXentry")

        group.create_dataset("definition", data=NX_APP_DEF_NAME)
        self._create_dataset(group, "experiment_description", experiment_description)
        self._create_dataset(group, "title", title)
        logger.debug("title: %s", title)

        # FIXME: Check NeXus structure: point to this group for default plot
        self._h5root.attrs["default"] = group.name.split("/")[-1]
        return group

    def create_xpcs_group(self,
                          h5parent,
                          g2: np.ndarray=None,
                          g2_stderr: np.ndarray=None,
                          g2_partials_twotime: np.ndarray=None,
                          g2_twotime: np.ndarray=None,
                          twotime: np.ndarray=None,
                          tau: np.ndarray=None,
                          mask: np.ndarray=None,
                          dqmap: np.ndarray=None,
                          dqlist: np.ndarray=None,
                          dphilist: np.ndarray=None,
                          sqmap: np.ndarray=None,
                          *args,
                          **kwargs):

        #TODO check units and use pint to convert
        # https://pint.readthedocs.io/en/stable/

        """
        see Data Solutions Pilot Meeting Notes
        """
        # md = md if md is not None else {}
        signal_dataset = None
        # check   input data
        for i in locals():
            if i is None:
                #TODO check what happens if type hint is violated
                warnings.warn(f'Did not received expected {i.__name__} data - '
                              f'Cannot write complete XPCS groups')
            # here we check the plottable data
            elif i in ("g2", "twotime", "tau"):
                signal_dataset = i.__name__

        xpcs_group = self._init_group(h5parent, "XPCS", "NXprocess")
        # TODO check if plottable data is assigned correctly
        if signal_dataset is None:
            warnings.warn(f'No plottable data available in {xpcs_group.__name__} cannot write signal attribute')
        else:
            # this defines the preferred plottable data
            xpcs_group.attrs["signal"] = signal_dataset

        # create datagroup and add datasets
        data_group = self._init_group(xpcs_group, "data", "NXdata")
        #FIXME add correct data path and units based on loader structure
        self._create_dataset(data_group, "g2", g2, units="au")
        self._create_dataset(data_group, "g2_stderr",  g2_stderr, units="au")
        self._create_dataset(data_group, "tau",  tau, units="au")

        # add twotime group and dataset
        twotime_group = self._init_group(xpcs_group, "twotime", "NXdata")
        self._create_dataset(twotime_group, "g2_partials_twotime", g2_partials_twotime, units="au")
        self._create_dataset(twotime_group, "g2_twotime", g2_twotime, units="au")
        # Twotime data should be a C-shaped 3D array
        # self._create_dataset(twotime_group, "C_0000X", C_0000X, units="au")

        #create instrument group and mask group, add datasets
        #TODO do we really want an instrument group here or direktly adding mask as a subentry?
        instrument_group = self._init_group(xpcs_group, "instrument", "NXdata")
        mask_group = self._init_group(instrument_group, "mask", "NXdata")
        self._create_dataset(mask_group, "mask", mask, units="au")
        self._create_dataset(mask_group, "dqmap", dqmap, units="au")
        self._create_dataset(mask_group, "dqlist", dqlist, units="au")
        self._create_dataset(mask_group, "dphilist", dphilist, units="au")
        self._create_dataset(mask_group, "sqmap", sqmap, units="au")


    def create_saxs_1d_group(self,
                             h5parent,
                             md=None,
                             I: np.ndarray=None,
                             I_partial: np.ndarray=None,
                             *args,
                             **kwargs):
        """
        see Data Solutions Pilot Meeting Notes
        """

        for i in locals():
            if i is None:
                #TODO check what happens if type hint is violated
                warnings.warn(f'Did not received expected {i.__name__} data - '
                              f'Cannot write complete SAXS 1D group')

        saxs_1d_group = self._init_group(h5parent, "SAXS_1D", "NXprocess")
        data_group = self._init_group(saxs_1d_group, "data", "NXdata")
        self._create_dataset(data_group, "I", I, units="au")
        self._create_dataset(data_group, "I_partial", I_partial, units="au")


    def create_saxs_2d_group(self,
                             h5parent,
                             md=None,
                             I:np.ndarray=None,
                             *args,
                             **kwargs):
        """
        see Data Solutions Pilot Meeting Notes
        """

        for i in locals():
            if i is None:
                #TODO check what happens if type hint is violated
                warnings.warn(f'Did not received expected {i.__name__} data - '
                              f'Cannot write complete SAXS 2D group')

        saxs_2d_group = self._init_group(h5parent, "SAXS_2D", "NXprocess")
        data_group = self._init_group(saxs_2d_group, "data", "NXdata")
        self._create_dataset(data_group, "I", I, units="au")


    def create_instrument_group(self,
                                h5parent,
                                md=None,
                                count_time: np.ndarray=None,
                                frame_time: np.ndarray=None,
                                description: str=None,
                                distance: float=None,
                                x_pixel_size: float=None,
                                y_pixel_size: float=None,
                                energy: float=None
                                ):
        """Write the NXinstrument group."""
        if "instrument" not in md:
            return
        md = md if md is not None else {}
        instrument_group = self._init_group(h5parent, "instrument", "NXinstrument")

        # create detector group and add datasets
        detector_group = self._init_group(instrument_group, "detector", "NXdetector")
        self._create_dataset(detector_group, "count_time", count_time, units="au")
        self._create_dataset(detector_group, "frame_time", frame_time, units="au")
        self._create_dataset(detector_group, "description", description, units="au")
        self._create_dataset(detector_group, "distance", distance, units="au")
        self._create_dataset(detector_group, "x_pixel_size", x_pixel_size, units="au")
        self._create_dataset(detector_group, "y_pixel_size", y_pixel_size, units="au")

        #create monochromator group and add datasets
        mono_group = self._init_group(instrument_group, "monochromator", "NXmonochromator")
        self._create_dataset(mono_group, "energy", energy, units="au")
