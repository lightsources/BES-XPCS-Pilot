#!/usr/bin/env python

"""
Write a NeXus file from the XPCS data

These files contain several sets of results, including:

* 1-D SAXS
* 2-D SAXS
* XPCS
* and may include other analyses
"""

import datetime
import logging
import os

import h5py
import numpy as np

logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)

A_KEV = 12.3984244  # voltage * wavelength product
NX_EXTENSION = ".nxs"   # .nxs is known by PyMCA, .nx is not (use generic filter then)


def write_file_header(h5parent):
    """optional header metadata"""
    timestamp = datetime.datetime.now().isoformat(sep=" ", timespec="seconds")
    logger.debug('timestamp: %s', str(timestamp))

    # give the HDF5 root some more attributes
    h5parent.attrs['file_name'] = h5parent.filename
    h5parent.attrs['file_time'] = timestamp
    h5parent.attrs['instrument'] = 'APS XPCS at 8-ID-I'
    h5parent.attrs['creator'] = __file__             # TODO: better choice?
    h5parent.attrs['HDF5_Version'] = h5py.version.hdf5_version
    h5parent.attrs['h5py_version'] = h5py.version.version


def create_entry_group(h5parent, md):
    """
    all information about the measurement

    see: https://manual.nexusformat.org/classes/base_classes/NXentry.html
    """
    nxentry = h5parent.create_group('entry')
    nxentry.attrs['NX_class'] = 'NXentry'

    title = os.path.splitext(md["datafilename"])[0]
    ds = nxentry.create_dataset('title', data=title)
    ds.attrs["target"] = ds.name      # we'll re-use this
    logger.debug("title: %s", title)

    # NeXus structure: point to this group for default plot
    h5parent.attrs['default'] = nxentry.name.split("/")[-1]

    return nxentry


def create_instrument_group(h5parent, md):
    """
    write the NXinstrument group

    see:https://manual.nexusformat.org/classes/base_classes/NXinstrument.html
    """
    nxinstrument = h5parent.create_group('instrument')
    nxinstrument.attrs['NX_class'] = 'NXinstrument'
    nxinstrument.attrs['canSAS_class'] = 'SASinstrument'
    nxinstrument.attrs['target'] = nxinstrument.name
    ds = nxinstrument.create_dataset('name', data="APS 8-ID-I XPCS")
    ds.attrs["short_name"] = "XPCS"

    # describe the X-ray source
    nxsource = nxinstrument.create_group('source')
    nxsource.attrs['NX_class'] = 'NXsource'
    nxsource.attrs['canSAS_class'] = 'SASsource'
    nxsource.attrs['target'] = nxsource.name
    nxsource.create_dataset('name', data="Advanced Photon Source")
    nxsource.create_dataset('probe', data="x-ray")
    ds = nxsource.create_dataset('type', data="Synchrotron X-ray Source")
    ds.attrs["target"] = ds.name              # for NeXus link

    def to_iso(timestring):
        """
        reformat timestring as ISO8601 format

        source: Tue Feb 18 15:30:30 2020
        result: 2020-02-18T15:30:30
        """
        source_format = '%a %b %d %H:%M:%S %Y'
        dt = datetime.datetime.strptime(timestring, source_format)
        return dt.isoformat()

    nxsource.create_dataset('start_time', data=to_iso(md["start_time"]))
    nxsource.create_dataset('end_time', data=to_iso(md["end_time"]))

    ds = nxsource.create_dataset('current_start', data=md["current_start"])
    ds.attrs['units'] = 'mA'
    ds.attrs['target'] = ds.name
    ds = nxsource.create_dataset('current_end', data=md["current_end"])
    ds.attrs['units'] = 'mA'
    ds.attrs['target'] = ds.name
    nxsource["current"] = nxsource["current_start"]

    # energy & wavelength are stored here
    nxmono = nxinstrument.create_group('monochromator')
    nxmono.attrs['NX_class'] = 'NXmonochromator'
    ds = nxmono.create_dataset('energy', data=md["energy"])
    ds.attrs['units'] = 'keV'
    ds.attrs["target"] = ds.name              # for NeXus link
    ds = nxmono.create_dataset('wavelength', data=A_KEV/md["energy"])
    ds.attrs['units'] = 'angstrom'
    ds.attrs["target"] = ds.name              # for NeXus link

    # NXcanSAS _requires_ a dataset called "radiation" in its NXsource
    # that takes the same values as "type _or_ "probe" in NXsource.
    # Here, we link radiation -> type
    nxsource["radiation"] = nxsource["type"]  # NeXus link to canSAS synonym

    # NXcanSAS says "incident_wavelength" is optional in the NXsource group
    # Here, we link to where wavelength has been given elsewhere
    # When we give an absolute HDF5 address, 
    # we can use any group as the parent
    wavelength = nxsource["/entry/instrument/monochromator/wavelength"]
    nxsource["incident_wavelength"] = wavelength

    return nxinstrument


def create_sample_group(h5parent, md, *args):
    """
    write the NXsample group

    see:https://manual.nexusformat.org/classes/base_classes/NXsample.html
    """
    group = h5parent.create_group('sample')
    group.attrs['NX_class'] = 'NXsample'
    group.attrs['target'] = group.name

    group["name"] = group["/entry/title"]   # use the entry group's title
    ds = group.create_dataset('thickness', data=md["sample_thickness"])
    ds.attrs["units"] = "mm"    # TODO: is it true?

    for k in """
            temperature_A
            temperature_A_set
            temperature_B
            temperature_B_set
            """.split():
        ds = group.create_dataset(k, data=md["sample_"+k])
        ds.attrs["units"] = "C"
        ds.attrs["target"] = ds.name
    group["temperature"] = group["temperature_A_set"]   # TODO: which one?

    for k in """
            orientation
            translation
            translation_table
            """.split():
        ds = group.create_dataset(k, data=md["sample_"+k])
        # TODO: description? units?

    return group


def store_saxs_1d(h5parent, xpcs, md, *args):
    """
    write the 1D SAXS data

    see: https://manual.nexusformat.org/classes/applications/NXcanSAS.html

    NXcanSAS describes more (optional) content.
    Here we write the minimum required.
    """
    group = h5parent.create_group('SAXS_1D')
    group.attrs['NX_class'] = 'NXsubentry'
    group.attrs['canSAS_class'] = 'SASentry'
    group.create_dataset('definition', data="NXcanSAS")

    group["run"] = group["/entry/title"]   # use the entry group's title
    group.create_dataset('title', data="static 1D SAXS from XPCS data")

    group.attrs['default'] = 'data'
    nxdata = group.create_group('data')
    nxdata.attrs['NX_class'] = 'NXdata'
    nxdata.attrs['canSAS_class'] = 'SASdata'
    nxdata.attrs['signal'] = 'I'
    nxdata.attrs['I_axes'] = 'Q'
    nxdata.attrs['Q_indices'] = [0,]

    ds = nxdata.create_dataset(
        'I', data=xpcs["Iq"][0],
        compression='gzip', compression_opts=9)
    ds.attrs["units"] = "arbitrary"
    ds.attrs["units_details"] = "Photon/Pixel/Frame"    # non-standard attribute!
    ds = nxdata.create_dataset(
        'Q', data=xpcs["ql_sta"],
        compression='gzip', compression_opts=9)
    ds.attrs["units"] = "1/angstrom"

    group["instrument"] = group["/entry/instrument"]
    group["sample"] = group["/entry/sample"]
    return group


def store_saxs_2d(h5parent, xpcs, md, mask, *args):
    """
    write the 2D SAXS data

    see: https://manual.nexusformat.org/classes/applications/NXcanSAS.html

    NXcanSAS describes more (optional) content.
    Here we write the minimum required.
    """
    group = h5parent.create_group('SAXS_2D')
    group.attrs['NX_class'] = 'NXsubentry'
    group.attrs['canSAS_class'] = 'SASentry'
    group.create_dataset('definition', data="NXcanSAS")

    group["run"] = group["/entry/title"]   # use the entry group's title
    group.create_dataset('title', data="static 2D SAXS from XPCS data")

    group.attrs['default'] = 'data'
    nxdata = group.create_group('data')
    nxdata.attrs['NX_class'] = 'NXdata'
    nxdata.attrs['canSAS_class'] = 'SASdata'
    nxdata.attrs['signal'] = 'I'
    # nxdata.attrs['I_axes'] = 'Q'  # TODO: get the Q values
    # nxdata.attrs['Q_indices'] = [0,]

    ds = nxdata.create_dataset(
        'I', data=xpcs["Int_2D"],
        compression='gzip', compression_opts=9)
    ds.attrs["units"] = "arbitrary"
    ds.attrs["units_details"] = "Photon/Pixel/Frame"    # non-standard attribute!
    # ds = nxdata.create_dataset(
    #     'Q', data=xpcs["ql_dyn"],
    #     compression='gzip', compression_opts=9)
    # ds.attrs["units"] = "1/angstrom"

    nxdata.attrs['mask'] = 'mask'
    # nxdata.attrs['Mask_indices'] = once we get a Q array
    # NXcanSAS mask: false (0) means no mask and true (1) means mask
    saxs_mask = np.where(mask > 0, 0, 1)
    ds = nxdata.create_dataset(
        'mask', data=saxs_mask,
        compression='gzip', compression_opts=9)
    ds.attrs['units'] = 'boolean'

    group["instrument"] = group["/entry/instrument"]
    group["sample"] = group["/entry/sample"]
    return group


def store_xpcs(h5parent, xpcs, md, mask, rois):
    """
    write the XPCS data

    see: XPCS definition not created yet
    """
    group = h5parent.create_group('XPCS')
    group.attrs['NX_class'] = 'NXprocess'  # no XPCS-specific NXDL yet
    # see: https://manual.nexusformat.org/classes/base_classes/NXprocess.html

    group["title"] = group["/entry/title"]   # use the entry group's title
    group.create_dataset('experiment_description', data="XPCS results")

    ###### create the NXdata group ######
    nxdata = group.create_group('data')
    nxdata.attrs['NX_class'] = 'NXdata'
    nxdata.attrs['target'] = nxdata.name    # for NeXus link
    group.attrs["default"] = "data"    # for NeXus default plot
    
    for k, v in xpcs.items():
        logger.debug("%s, shape=%s, dtype=%s", k, str(v.shape), str(v.dtype))

    ###### signal data ######
    # QZ: I believe a 3D array should suffice.
    #   The three dimensions are Q, phi and delay time.
    # PJ: we don't have phi now, show how to write for 2D array
    nxdata.attrs['signal'] = 'g2'      # local name of signal data
    nxdata.attrs['axes'] = 't_el:ql_dyn'
    signal = nxdata.create_dataset(
        'g2',
        data=xpcs["g2"],
        compression='gzip',
        compression_opts=9)
    signal.attrs['units'] = 'scale'
    signal.attrs['long_name'] = 'XPCS g2(t, Q)'    # suggested Y axis plot label
    ds = nxdata.create_dataset(
        'g2_errors',
        data=xpcs["g2_err"],
        compression='gzip',
        compression_opts=9)
    ds.attrs['units'] = 'scale'
    ds = nxdata.create_dataset(
        't_el',
        data=xpcs["t_el"],
        compression='gzip',
        compression_opts=9)
    ds.attrs['units'] = 's'
    ds = nxdata.create_dataset(
        'ql_dyn',
        data=xpcs["ql_dyn"],
        compression='gzip',
        compression_opts=9)
    ds.attrs['units'] = '1/angstrom'

    ###### define the mask(s) in NXarraymask group ######
    masks = nxdata.create_group('masks')
    masks.attrs['NX_class'] = 'NXnote'  # TODO: what class is this?

    nxmask = masks.create_group('mask')
    nxmask.attrs['NX_class'] = 'NXarraymask'
    nxmask.create_dataset('usage', data="Selective")
    # mask_names is not in the NXDL, that's OK
    nxmask.create_dataset('mask_names', data=mask_names)
    nxmask.create_dataset(
        'mask',
        data=mask,
        compression='gzip',
        compression_opts=5)   # compresses about 1000x!

    rois = nxdata.create_group('rois')
    rois.attrs['NX_class'] = 'NXnote'  # TODO: what class is this?

    for roi in rois:
        roi_group = rois.create_group('roi_1')
        roi_group.attrs['NX_class'] = 'NXparameterizedmask'
        roi_group.attrs['data_link'] = ''  # TODO: get nexus path to raw data
        roi_group.attrs['usage'] = 'selective'
        roi_group.attrs.update(roi)
        roi_group.attrs['annotation'] = f"A {roi.pop('type')} roi with parameters: {str(roi)}"

    nxmask["data_link"] = nxmask[signal.name]   # NeXus hard link
    signal.attrs['target'] = signal.name    # required by NeXus

    group["instrument"] = group["/entry/instrument"]
    group["sample"] = group["/entry/sample"]
    return group


def write_metadata(parent, md):
    """
    write metadata
    """
    logger.debug('write metadata group')

    nxnote = parent.create_group('metadata')
    nxnote.attrs['NX_class'] = 'NXnote'
    for k, v in md.items():
        nxnote.create_dataset(k, data=v)
    
    return nxnote


def write_nx_file(nx_file, xpcs, qmap, mask, mask_names, rois, md):
    """
    write the NeXus data file
    """
    logger.info('write NeXus file: %s', nx_file)

    with h5py.File(nx_file, "w") as nx:
        write_file_header(nx)
        nxentry = create_entry_group(nx, md)

        nxinstrument = create_instrument_group(nxentry, md)
        nxsample = create_sample_group(nxentry, md)
        write_metadata(nxentry, md)

        nxsaxs1d = store_saxs_1d(nxentry, xpcs, md)
        nxsaxs2d = store_saxs_2d(nxentry, xpcs, md, mask)
        nxxpcs = store_xpcs(nxentry, xpcs, md, mask, mask_names, rois)

        # use XPCS/data as the default /entry/data for default plot
        nxentry["data"] = nxxpcs["data"]    # HDF5 hard link
        nxentry.attrs['default'] = 'data'
