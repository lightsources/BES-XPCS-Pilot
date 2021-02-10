#!/usr/bin/env python

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
        group = self._init_group(self._h5root, entry_name, "NXentry", md)
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

    def create_xpcs_data_group(self, h5parent, md=None, count_entry=None):
        group, md = self._init_group(h5parent, "data", "NXsubentry", md)

        ds = group.create_dataset("g2", data=md["XPCS"]["g2"])
        ds.attrs["units"] = "a.u."
        ds.attrs["target"] = ds.name

        ds = group.create_dataset("g2_stderr", data=md["XPCS"]["g2_stderr"])
        ds.attrs["units"] = "a.u."
        ds.attrs["target"] = ds.name

        ds = group.create_dataset("tau", data=md["XPCS"]["tau"])
        ds.attrs["units"] = "a.u."
        ds.attrs["target"] = ds.name

    def _create_dataset(self, h5parent, name, md_path, **kwargs):
        """
        use this to create datasets in different (sub-)groups
        """
        ds = h5parent.create_dataset(name, data=self.md[md_path])
        for k, v in kwargs.items():
            ds.attrs[k] = v
        # ds.attrs["units"] = **kwargs.items()  # FIXME allow for other units
        ds.attrs["target"] = ds.name
        return ds

    def create_xpcs_group(self, h5parent, md=None, *args, **kwargs):
        """
        see Data Solutions Pilot Meeting Notes
        """
        md = self._init_md(md)
        xpcs_group = self._init_group(h5parent, "XPCS", "NXprocess")
        #this defines the preferred plot data
        xpcs_group.attrs["default"] = "data"

        data_group = self._init_group(xpcs_group, "data", "NXdata")
        twotime_group = self._init_group(xpcs_group, "twotime", "NXdata")

        #FIXME add correct data path and units based on loader structure
        self._create_dataset(data_group, "g2", "md_path", units="au")
        self._create_dataset(data_group, "g2_stderr", "md_path", units="au")
        self._create_dataset(data_group, "tau", "md_path", units="au")

        self._create_dataset(twotime_group, "g2_partials_twotime", "md_path", units="au")
        self._create_dataset(twotime_group, "g2_twotime", "md_path", units="au")

        #TODO: work out how to name this and iterate through the datasets
        # will it be n datasets or an n dimensional array
        # 
        # for n in number_of_entries_from_dict:
        #     add _create_dataset
        self._create_dataset(twotime_group, "C_0000X", "md_path", units="au")


    def create_saxs_1d_group(self, h5parent, md=None, *args, **kwargs):
        """
        see Data Solutions Pilot Meeting Notes
        """
        if "SAXS_1D" not in md:
            return
        group, md = self._init_group(h5parent, "SAXS_1D", "NXsubentry", md)
        # TODO load actual md dict to add the data
        # FIXME create small "create_dataset" helper function
        # for adding data in 1 line
        ds = group.create_dataset("I", data=md["SAXS_1D"]["I"])
        ds.attrs["units"] = "counts"
        ds.attrs["target"] = ds.name

        ds = group.create_dataset("I_partial", data=md["SAXS_1D"]["partial"])
        ds.attrs["units"] = "counts"
        ds.attrs["target"] = ds.name

    def create_saxs_2d_group(self, h5parent, md=None, *args, **kwargs):
        if "SAXS_2D" not in md:
            return
        group, md = self._init_group(h5parent, "SAXS_2D", "NXsubentry", md)

        ds = group.create_dataset("I", data=md["SAXS_2D"]["I"])
        ds.attrs["units"] = "counts"
        ds.attrs["target"] = ds.name




    def create_instrument_group(self, h5parent, md=None, count_entry=None):
        """Write the NXinstrument group."""

        if "instrument" not in md:
            return

        # TODO: will need to get and add data
        group, md = self._init_group(
            h5parent, "instrument", "NXinstrument", md
        )

        name_field = md["instrument"]["name"]
        ds = group.create_dataset("name", data=name_field)
        ds.attrs["target"] = ds.name  # we'll re-use this
        logger.debug("instrument: %s", name_field)

        # TODO allow to add different detector group data
        # self.create_detector_group(group, "detector_2", md=md)
        # self._create_monitor_group(group, "monitor", md=md)
