#!/usr/bin/env python
import datetime
import h5py
import logging
import numpy as np
import warnings
import pint

logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)

A_KEV = 12.3984244  # voltage * wavelength product
# .nxs is known by PyMCA, .nx is not (use generic filter then)
NX_EXTENSION = ".nxs"
NX_APP_DEF_NAME = "NXxpcs"  # name of NeXus Application Definition


#TODO: not defined in NeXus at this time
# Need to create & propose this new Application Definition to NIAC


class NXCreator:
    """
    Write a NeXus file from the XPCS and SAXS data Using NXxpcs and NXcansas definition

    These files contain several sets of results, including:
    * XPCS
    * 1-D SAXS
    * 2-D SAXS
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
        with h5py.File(self._output_filename, "w") as self.file:
            self.write_file_header(self.file)
            self.file.close()

    def write_file_header(self, output_file):
        """optional header metadata"""
        timestamp = datetime.datetime.now().isoformat(sep=" ", timespec="seconds")
        logger.debug("timestamp: %s", str(timestamp))
        # give the HDF5 root some more attributes
        #TODO move instrument name to instrument group
        # output_file.attrs["instrument"] = instrument_name
        output_file.attrs["file_name"] = output_file.filename
        output_file.attrs["file_time"] = timestamp
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

    def _check_units(self, name, expected, supplied):
        """
        units check for supplied units

        Our test for units should check if the supplied
        units string can be mapped into the expected units for that field.
        If arbitrary units are supplied in form of 'au', 'a.u.' or 'a.u' no conversion is applied
        and pint if not used for the units check.

        :param : name of field
        :param : expected units
        :param : units string that was given
        :return *bool*: `True` if units conversion is possible:
        """

        # catch arbitrary units separately from pint --> point that out in documentation
        if supplied in ['au', 'a.u.', 'a.u']:
            logger.info("Info: arbitrary units supplied for '%s' in form of '%s' np units conversion applicable",
                        name,
                        supplied)
            return True
        else:
            ureg = pint.UnitRegistry()
            user = 1.0 * ureg(supplied)
            try:
                user.to(expected)
                return True
            except pint.DimensionalityError:
                logger.warning("WARNING: '%s': Supplied units (%s) does not match expected units (%s)",
                               name,
                               supplied,
                               expected)
                return False


    def create_data_with_units(self, group, name, value, expected, supplied):

        if self._check_units(name, expected, supplied):
            self._create_dataset(group, name, value, units=supplied)
        else:
            self._create_dataset(group, name, value)


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

            entry_group.create_dataset("definition", data=NX_APP_DEF_NAME)
            if experiment_description is not None:
                experiment_description = experiment_description
            else:
                experiment_description = 'Default XPCS experiment'
            self._create_dataset(entry_group, "experiment_description", experiment_description)
            title = title if title is not None else "default"
            self._create_dataset(entry_group, "title", title)
            logger.debug("title: %s", title)
            # Point to this group for default plot
            file.attrs["default"] = entry_group.name


    def create_xpcs_group(self,
                          g2: np.ndarray = None,
                          g2_units: str = 'a.u',
                          g2_stderr: np.ndarray = None,
                          g2_partials_twotime: np.ndarray = None,
                          g2_partials_twotime_units: str = 'a.u.',
                          g2_twotime: np.ndarray = None,
                          g2_twotime_units: str = 'a.u.',
                          C2: np.ndarray = None,
                          C2_units: str = 'a.u.',
                          # TODO: decide on name for this time, see comment in xml file
                          tau: np.ndarray = None,
                          tau_units: str = 's',
                          frame_sum: np.ndarray = None,
                          mask: np.ndarray = None,
                          dqmap: np.ndarray = None,
                          dqlist: np.ndarray = None,
                          dphilist: np.ndarray = None,
                          sqmap: np.ndarray = None,
                          sqlist: np.ndarray = None,
                          *args,
                          **kwargs):
        """
        See NXxpcs definition for details

        :param : g2 are values for the one-dimensional correlation as function of delay time (tau)
        :param : g2_units units for g2 is usually "a.u." (arbitrary units)
        :param : g2_stderr are the standard deviation error values for the g2 correlation values
        :param : g2_partials_twotime is the sum across the diagonals of C2
        :param : g2_partials_twotime_units subsets of the sum across the diagonals of C2
        :param : C2 is the two-dimensional Twotime correlation
        :param : C2_units units for C2 is usually arbitrary units
        :param : tau is the delay time corresponding to the g2 correlation values
        :param : tau_units any time units
        :param : frame_sum is the twodimensional average along the frames stack
        :param : mask is a two-dimensional array of the same shape as the data frames that masks valid and invalid pixel
                 such as broken pixels, beamstop etc
        :param : dqmap is a two-dimensional map of q bins indexed from 0 to N (number of q bins)
        :param : dqlist is a list of the q values for the multiple g2 correlation curves
        :param : dphilist is a list of the phi values
        :param : sqmap is a two-dimensional map of q bins indexed from 0 to N (number of q bins)
        :param : sqlist
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
            #check that plottable data is assigned correctly
            if signal_dataset is None:
                warnings.warn(f'No plottable data available in {self.xpcs_group.__name__} cannot write signal attribute')
            else:
                # this defines the preferred plottable data
                self.xpcs_group.attrs["signal"] = signal_dataset

            # create datagroup and add datasets
            data_group = self._init_group(self.xpcs_group, "data", "NXdata")

            self.create_data_with_units(data_group, "g2", g2, 'a.u.', supplied=g2_units)
            self.create_data_with_units(data_group, "g2_stderr", g2_stderr, 'a.u.', supplied=g2_units)
            self.create_data_with_units(data_group, "tau", tau, 's', supplied=tau_units)
            # add twotime group and dataset
            twotime_group = self._init_group(self.xpcs_group, "twotime", "NXdata")
            self.create_data_with_units(twotime_group, "g2_partials_twotime", g2_partials_twotime, 'a.u.',
                                       supplied=g2_partials_twotime_units)
            self.create_data_with_units(twotime_group, "g2_twotime", g2_twotime, 'a.u.', supplied=g2_twotime_units)
            # TODO find a better name for this entry: e.g. twotime_corr, twotime, C2T_all...?
            self.create_data_with_units(twotime_group, "C2", C2, 'a.u.', supplied=C2_units)

            # create instrument group and mask group, add datasets
            # TODO do we really want an instrument group here or directly adding mask as a subentry?
            instrument_group = self._init_group(self.xpcs_group, "instrument", "NXdata")
            mask_group = self._init_group(instrument_group, "masks", "NXdata")
            self._create_dataset(mask_group, "mask", mask, units="au")
            self._create_dataset(mask_group, "dqmap", dqmap)
            self._create_dataset(mask_group, "dqlist", dqlist, units="1/Angstrom")
            self._create_dataset(mask_group, "dphilist", dphilist, units="1/Angstrom")
            self._create_dataset(mask_group, "sqmap", sqmap)
            self._create_dataset(mask_group, "sqlist", sqlist, units="1/Angstrom")
            file.close()


    def create_saxs_1d_group(self,
                             I: np.ndarray = None,
                             I_units: str = None,
                             Q: np.ndarray = None,
                             Q_units: str = None,
                             I_partial: np.ndarray = None,
                             I_partial_units: str = None,
                             *args,
                             **kwargs):
        """
        See NXcansas definition

        :param : I azimuthally integrated intensity
        :param : I_units units for the azimuthally integrated intensity
        :param : Q the q value corresponding to the azimuthally integrated intensity values
        :param : Q_units units in reciprocal space
        :param : I_partial units in reciprocal space
        :param : I_partial_units units in reciprocal space
        """

        for i in locals():
            if i is None:
                # TODO check what happens if type hint is violated
                warnings.warn(f'Did not received expected {i.__name__} data - '
                              f'Cannot write complete SAXS 1D group')
        with h5py.File(self._output_filename, "a") as file:
            saxs_1d_group = self._init_group(file[self.entry_group_name], "SAXS_1D", "NXprocess")
            data_group = self._init_group(saxs_1d_group, "data", "NXdata")
            self.create_data_with_units(data_group, "I", I, 'a.u.', supplied=I_units)
            self.create_data_with_units(data_group, 'Q', Q, '1/angstrom', supplied=Q_units)
            self.create_data_with_units(data_group, "I_partial", I_partial, 'a.u.', supplied=I_partial_units)



    def create_saxs_2d_group(self,
                             I: np.ndarray = None,
                             *args,
                             **kwargs):
        """
        See NXcansas definition

        :param : I is the averaged intensity olong the twodimensional stack of frames
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


    def create_instrument_group(self,
                                instrument_name: str = None,
                                count_time: np.ndarray = None,
                                count_time_units: str = None,
                                frame_time: np.ndarray = None,
                                frame_time_units: str = None,
                                description: str = None,
                                distance: float = None,
                                distance_units: str = None,
                                x_pixel_size: float = None,
                                y_pixel_size: float = None,
                                pixel_size_units: str = None,
                                beam_center_x: float = None,
                                beam_center_units: str = None,
                                beam_center_y: float = None,
                                energy: float = None,
                                energy_units: str = None,
                                ):
        """
        Write the NXinstrument group. See NXxpcs definition

        :param : instrument_name a descriptive name of the instrument the data originates from
        :param : count_time is the exposure time of each frame
        :param : count_time_units in units of time
        :param : frame_time is the exposure period of frames i.e. the time between frame starts
        :param : frame_time_units in units of time
        :param : description is the detector name and/or manufacturer
        :param : distance is the distance between the sample and the detector
        :param : distance_units in units of length
        :param : x_pixel_size pixel size of the detector in x direction
        :param : y_pixel_size pixel size of the detector in y direction
        :param : pixel_size_units in units of length
        :param : beam_center_x is the position of beam center in detector's coordinates in x direction
        :param : beam_center_y is the position of beam center in detector's coordinates in y direction
        :param : beam_center_units in pixel
        :param : energy is the photon energy of the incident beam
        :param : energy_units in units of energy
        """

        with h5py.File(self._output_filename, "a") as file:
            self.instrument_group = self._init_group(file[self.entry_group_name], "instrument", "NXinstrument")
            #TODO how to add instrument name here
            # self.instrument_group.attrs["instrument"] = instrument_name

            # create detector group and add datasets
            detector_group = self._init_group(self.instrument_group, "detector", "NXdetector")
            self.create_data_with_units(detector_group, "count_time", count_time, 's', supplied=count_time_units)
            self.create_data_with_units(detector_group, "frame_time", frame_time, 's', supplied=frame_time_units)
            self._create_dataset(detector_group, "description", description)
            self.create_data_with_units(detector_group, "distance", distance, 'mm', supplied=distance_units)
            self.create_data_with_units(detector_group, "x_pixel_size", x_pixel_size, 'um', supplied=pixel_size_units)
            self.create_data_with_units(detector_group, "y_pixel_size", y_pixel_size, 'um', supplied=pixel_size_units)
            self.create_data_with_units(detector_group, "beam_center_x", beam_center_x, 'pixel', supplied=beam_center_units)
            self.create_data_with_units(detector_group, "beam_center_y", beam_center_y, 'pixel', supplied=beam_center_units)

            # create monochromator group and add datasets
            mono_group = self._init_group(self.instrument_group, "monochromator", "NXmonochromator")
            self.create_data_with_units(mono_group, "energy", energy, 'eV', supplied=energy_units)


