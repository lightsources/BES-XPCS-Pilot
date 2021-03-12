#!/usr/bin/env python
import logging

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

    def _init_md(self, md=None):
        if md is None:
            md = {}
        return md

    def create_entry_group(self, md=None, count_entry=None):
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
        md = self._init_md(md)

        group.create_dataset("definition", data=NX_APP_DEF_NAME)
        experiment_description = md.get("experiment_description")
        if experiment_description is not None:
            group.create_dataset(
                "experiment_description", data=experiment_description
            )

        title = md.get("title", "")
        ds = group.create_dataset("title", data=title)
        ds.attrs["target"] = ds.name  # we'll re-use this
        logger.debug("title: %s", title)

        # NeXus structure: point to this group for default plot
        self._h5root.attrs["default"] = group.name.split("/")[-1]

        return group


    def _create_dataset(self, group, name, md_path, **kwargs):
        """
        use this to create datasets in different (sub-)groups
        """
        ds = group.create_dataset(name, data=md_path)
        for k, v in kwargs.items():
            ds.attrs[k] = v
        ds.attrs["target"] = ds.name
        return ds

    def create_xpcs_group(self, h5parent, md=None, *args, **kwargs):
        """
        see Data Solutions Pilot Meeting Notes
        """
        md = self._init_md(md)
        xpcs_group = self._init_group(h5parent, "XPCS", "NXprocess")
        # TODO check if plottable data is assigned correctly
        #this defines the preferred plot data
        xpcs_group.attrs["default"] = "data"

        # create datagroup and add datasets
        data_group = self._init_group(xpcs_group, "data", "NXdata")
        #FIXME add correct data path and units based on loader structure
        self._create_dataset(data_group, "g2", md["g2"], units="au")
        self._create_dataset(data_group, "g2_stderr",  md["g2_stderr"], units="au")
        self._create_dataset(data_group, "tau",  md["tau"], units="au")

        # add twotime group and dataset
        twotime_group = self._init_group(xpcs_group, "twotime", "NXdata")
        self._create_dataset(twotime_group, "g2_partials_twotime", md["g2_partials_twotime"], units="au")
        self._create_dataset(twotime_group, "g2_twotime", md["g2_twotime"], units="au")
        # Twotime data should be a C-shaped 3D array
        # self._create_dataset(twotime_group, "C_0000X", md["C_0000X"], units="au")

        #create instrument group and mask group, add datasets
        #TODO do we really want an instrument group here or direktly adding mask as a subentry?
        instrument_group = self._init_group(xpcs_group, "twotime", "NXdata")
        mask_group = self._init_group(instrument_group, "twotime", "NXdata")
        self._create_dataset(mask_group, "mask", md["mask"], units="au")
        self._create_dataset(mask_group, "dqmap", md["dqmap"], units="au")
        self._create_dataset(mask_group, "dqlist", md["dqlist"], units="au")
        self._create_dataset(mask_group, "dphilist", md["dphilist"], units="au")
        self._create_dataset(mask_group, "sqmap", md["sqmap"], units="au")


    def create_saxs_1d_group(self, h5parent, md=None, *args, **kwargs):
        """
        see Data Solutions Pilot Meeting Notes
        """
        if "SAXS_1D" not in md:
            return
        md = self._init_md(md)
        saxs_1d_group = self._init_group(h5parent, "SAXS_1D", "NXprocess")

        # create datagroup and add datasets
        data_group = self._init_group(saxs_1d_group, "data", "NXdata")
        self._create_dataset(data_group, "I", md["I"], units="au")
        self._create_dataset(data_group, "I_partial", md["I_partial"], units="au")


    def create_saxs_2d_group(self, h5parent, md=None, *args, **kwargs):
        if "SAXS_2D" not in md:
            return
        md = self._init_md(md)
        saxs_2d_group = self._init_group(h5parent, "SAXS_2D", "NXprocess")

        # create datagroup and add datasets
        data_group = self._init_group(saxs_2d_group, "data", "NXdata")
        self._create_dataset(data_group, "I", md["I"], units="au")


    def create_instrument_group(self, h5parent, md=None, count_entry=None):
        """Write the NXinstrument group."""
        if "instrument" not in md:
            return
        md = self._init_md(md)
        instrument_group = self._init_group(h5parent, "instrument", "NXinstrument")

        # create detector group and add datasets
        detector_group = self._init_group(instrument_group, "detector", "NXdetector")
        self._create_dataset(detector_group, "count_time", md["count_time"], units="au")
        self._create_dataset(detector_group, "frame_time", md["frame_time"], units="au")
        self._create_dataset(detector_group, "description", md["description"], units="au")
        self._create_dataset(detector_group, "distance", md["distance"], units="au")
        self._create_dataset(detector_group, "x_pixel_size", md["x_pixel_size"], units="au")
        self._create_dataset(detector_group, "y_pixel_size", md["y_pixel_size"], units="au")

        #create monochromator group and add datasets
        mono_group = self._init_group(instrument_group, "monochromator", "NXmonochromator")
        self._create_dataset(mono_group, "energy", md["energy"], units="au")