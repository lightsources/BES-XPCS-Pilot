#!/usr/bin/env python

"""
prepare an example NeXus file
"""

import datetime
import logging
import os

import h5py
import matplotlib.pyplot as plt
import numpy as np

import loaders

DATAFILE = 'B009_Aerogel_1mm_025C_att1_Lq0_001_0001-10000.hdf'
NEXUSFILE = 'NeXus_file.hdf'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def plot_qmap(dqmap, mask):
    """
    plot the Q map to PDF file
    """
    logger.info('plot Q map to file: Q_Map.pdf')
    fig, ax = plt.subplots(1, 1, figsize=(15, 10))
    im = ax.imshow(dqmap, cmap='jet', interpolation='none')
    fig.colorbar(im, ax=ax)
    plt.rc('font', size=20)
    plt.savefig('Q_Map.pdf', dpi=100, format='pdf', facecolor='w', edgecolor='w', transparent=False)

    logger.info('masks: %g Map', np.max(dqmap))
    logger.info('rows: %d Map', dqmap.shape[0])
    logger.info('columns: %d Map', dqmap.shape[1])

    ###### plot the masks to PDF file ######
    logger.info('plot mask to file: tmp.pdf')
    fig, ax = plt.subplots(1, 1, figsize=(15, 10))
    mask_10 = np.where(mask == 10, 1, 0)
    im = ax.imshow(mask_10, cmap='gray', interpolation='none')
    fig.colorbar(im, ax=ax)
    plt.rc('font', size=20)
    plt.savefig('tmp.pdf', dpi=100, format='pdf', facecolor='w', edgecolor='w', transparent=False)


def write_nexus_file(mask, mask_names, md):
    """
    demonstration: write a NeXus data file
    """
    fn_dir = os.path.dirname(__file__)
    nexus_file = os.path.join(fn_dir, NEXUSFILE)
    timestamp = datetime.datetime.now().isoformat(sep=" ", timespec="seconds")
    logger.info('write NeXus file: %s', NEXUSFILE)

    with h5py.File(nexus_file, "w") as nx:
        ###### optional header metadata ######
        # give the HDF5 root some more attributes
        nx.attrs['file_name'] = nexus_file
        nx.attrs['file_time'] = timestamp
        nx.attrs['instrument'] = 'APS XPCS at 8-ID-I'
        nx.attrs['creator'] = __file__             # TODO: better choice?
        nx.attrs['HDF5_Version'] = h5py.version.hdf5_version
        nx.attrs['h5py_version'] = h5py.version.version

        ###### create the NXentry group ######
        nx.attrs['default'] = 'entry' # point to this group for default plot
        nxentry = nx.create_group('entry')
        nxentry.attrs['NX_class'] = 'NXentry'
        nxentry.create_dataset('title', data=DATAFILE)     # TODO: better choice?

        ###### create the NXdata group ######
        nxentry.attrs['default'] = 'data'   # point to this group for default plot
        nxdata = nxentry.create_group('data')
        nxdata.attrs['NX_class'] = 'NXdata'

        ###### signal data ######
        nxdata.attrs['signal'] = 'image'      # local name of signal data
        signal = nxdata.create_dataset(
            'image',
            data=list(range(8)),  # FIXME: use actual image data
            compression='gzip',
            compression_opts=9)
        signal.attrs['units'] = 'scale'
        signal.attrs['long_name'] = 'FIXME: XPCS image data'    # suggested Y axis plot label

        ###### define the mask(s) in NXarraymask group ######
        nxmask = nxdata.create_group('mask')
        nxmask.attrs['NX_class'] = 'NXarraymask'
        nxmask.create_dataset('usage', data="Selective")   # TODO: check this
        # mask_names is not in the NXDL, that's OK
        nxmask.create_dataset('mask_names', data=mask_names)
        nxmask.create_dataset(
            'mask',
            data=mask,
            compression='gzip',
            compression_opts=5)   # compresses about 1000x!
        nxmask["data_link"] = nx[signal.name]   # make the hard link
        signal.attrs['target'] = signal.name    # required by NeXus

        ###### mask-related annotations in NXnote group ######
        nxnote = nxmask.create_group('annotation')
        nxnote.attrs['NX_class'] = 'NXnote'
        # writing generic metadata here for demonstration only
        # TODO: move this md to other places in the NeXus structure
        for k, v in md.items():
            nxnote.create_dataset(k, data=v)


def main():
    """
    read the QMap file, make plots, write the NeXus file
    """
    fn_dir = os.path.dirname(__file__)
    full_filename = os.path.join(fn_dir, DATAFILE)

    dqmap = loaders.read_qmap(full_filename)
    md = loaders.read_metadata(full_filename)
    mask, mask_names = loaders.compute_mask(dqmap)
    plot_qmap(dqmap, mask)
    write_nexus_file(mask, mask_names, md)


if __name__ == "__main__":
    main()
