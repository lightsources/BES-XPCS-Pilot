#!/usr/bin/env python

# import datetime
# import h5py
import logging

# import numpy as np
# import os

logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)

A_KEV = 12.3984244  # voltage * wavelength product
NX_EXTENSION = (
    ".nxs"  # .nxs is known by PyMCA, .nx is not (use generic filter then)
)

NX_APP_DEF_NAME = "NXxpcs"  # name of NeXus Application Definition
# TODO: not defined in NeXus at this time
# Need to create & propose this new Application Definition to NIAC


class NX_Creator:
    """

    Write a NeXus file from the XPCS data

    These files contain several sets of results, including:

    * 1-D SAXS
    * 2-D SAXS
    * XPCS
    * and may include other analyses

    """

    def __init_group__(self, h5parent, nm, NX_class, md=None):
        """Common steps to initialize a NeXus HDF5 group."""
        if md is None:
            md = {}

        group = h5parent.create_group(nm)
        group.attrs["NX_class"] = NX_class
        return group, md

    def create_entry_group(self, h5parent, md=None, count_entry=None):
        """
        all information about the measurement

        see: https://manual.nexusformat.org/classes/base_classes/NXentry.html
        """
        group, md = self.__init_group__(
            h5parent, f"entry_{count_entry}", "NXentry", md
        )
        # print('group', group, 'md', md)

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
        h5parent.attrs["default"] = group.name.split("/")[-1]

        self.create_instrument_group(group, md=md, count_entry=count_entry)
        self.create_xpcs_group(group, md=md, count_entry=count_entry)
        self.create_saxs_1d_group(group, md=md, count_entry=count_entry)
        self.create_saxs_2d_group(group, md=md, count_entry=count_entry)

        return group

    def create_instrument_group(self, h5parent, md=None, count_entry=None):
        """Write the NXinstrument group."""
        # TODO: will need to get and add data
        group, md = self.__init_group__(
            h5parent, "instrument", "NXinstrument", md
        )

        name_field = md.get("instrument", "")[f"entry_{count_entry}"]
        ds = group.create_dataset("name", data=name_field)
        ds.attrs["target"] = ds.name  # we'll re-use this
        logger.debug("instrument: %s", name_field)

        self.create_beam_group(group, "beam", md=md, count_entry=count_entry)
        self.create_detector_group(
            group, "detector_1", md=md, count_entry=count_entry
        )
        # TODO allow to add different detector group data
        # self.create_detector_group(group, "detector_2", md=md)
        self.create_monitor_group(group, "monitor", md=md)
        for n in range(md["translation"][f"entry_{count_entry}"].shape[1]):
            self.create_positioner_group(
                group,
                f"positioner_{n+1}",
                count_entry=count_entry,
                count_positioner=n,
                md=md,
            )

    def create_xpcs_group(self, h5parent, md=None, *args, **kwargs):
        """
        see Data Solutions Pilot Meeting Notes
        """
        group, md = self.__init_group__(h5parent, "XPCS", "NXsubentry", md)

    def create_saxs_1d_group(self, h5parent, md=None, *args, **kwargs):
        """
        see Data Solutions Pilot Meeting Notes
        """
        group, md = self.__init_group__(h5parent, "SAXS_1D", "NXsubentry", md)
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
        group, md = self.__init_group__(h5parent, "SAXS_2D", "NXsubentry", md)

        ds = group.create_dataset("I", data=md["SAXS_2D"]["I"])
        ds.attrs["units"] = "counts"
        ds.attrs["target"] = ds.name
