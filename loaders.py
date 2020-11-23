#!/usr/bin/env python

"""
load various components of XPCS data

.. autosummary::
   
    ~compute_mask
    ~read_metadata
    ~read_qmap
    ~read_xpcs_results
"""

import datetime
import logging
import os

import h5py
import matplotlib.pyplot as plt
import numpy as np

DATAFILE = 'B009_Aerogel_1mm_025C_att1_Lq0_001_0001-10000.hdf'
NEXUSFILE = 'NeXus_file.hdf'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def compute_mask(dqmap):
    """
    build the masks
    """
    number_of_masks = dqmap.max()
    if dqmap.min() == 0:
        number_of_masks += 1

    # encode these strings for HDF
    mask_names = [
        f"mask_{ii}".encode() 
        for ii in range(number_of_masks)
    ]

    # dqmap is already in the format of a Selective mask
    mask = np.array(dqmap)

    return mask, mask_names


def read_metadata(full_filename):
    """
    reads the QMap file, returns `md` dictionary
    """

    def get_key(key):
        v = result[key][()]
        if isinstance(v, np.ndarray):
            if v.shape == tuple([1, 1]):
                v = v[0]     # unpack the scalar from DataExchange convention
        elif isinstance(v, bytes):
            # convert b'string' to 'string'
            v = v.decode()
        return v

    md = {}
    with h5py.File(full_filename, 'r') as result:
        md["file_name"] = DATAFILE
        md["start_time"] = get_key("/measurement/instrument/source_begin/datetime")
        md["end_time"] = get_key("/measurement/instrument/source_end/datetime")
        md["current_start"] = get_key("/measurement/instrument/source_begin/current")
        md["current_end"] = get_key("/measurement/instrument/source_end/current")
        md["energy"] = get_key("/measurement/instrument/source_begin/energy")

        for key in """
                data_folder
                datafilename
                parent_folder
                root_folder
                specfile
                """.split():
            md[key] = get_key(f"/measurement/instrument/acquisition/{key}")

        for key in """
                manufacturer
                geometry
                adu_per_photon
                distance
                exposure_time
                exposure_period
                gain
                sigma
                x_binning
                x_dimension
                x_pixel_size
                y_binning
                y_dimension
                y_pixel_size""".split():
            md[key] = get_key(f"/measurement/instrument/detector/{key}")

        for key in """
                Version
                analysis_type
                input_file_local
                normalization_method
                """.split():
            md[f"xpcs_{key}"] = get_key(f"/xpcs/{key}")

        for key in """
                orientation
                temperature_A
                temperature_A_set
                temperature_B
                temperature_B_set
                thickness
                translation
                translation_table
                """.split():
            md[f"sample_{key}"] = get_key(f"/measurement/sample/{key}")

    return md


def read_qmap(full_filename):
    """
    reads the QMap from the DataExchange file, returns `dqmap`
    """
    with h5py.File(full_filename, 'r') as result:
        dqmap = np.squeeze(result.get('/xpcs/dqmap')[()])

    return dqmap


def read_xpcs_results(full_filename):
    """
    Read HDF file, return results
    """
    with h5py.File(full_filename, 'r') as f:
        Iq = f.get('/exchange/partition-mean-total')[()]
        I_partial = f.get('/exchange/partition-mean-partial')[()]
        ql_sta = np.squeeze(f.get('/xpcs/sqlist')[()])
        ql_dyn = np.squeeze(f.get('/xpcs/dqlist')[()])
        t0 = np.squeeze(f.get('/measurement/instrument/detector/exposure_period')[()])
        t_el = t0*np.squeeze(f.get('/exchange/tau')[()])
        g2 = f.get('/exchange/norm-0-g2')[()]
        g2_err = f.get('/exchange/norm-0-stderr')[()]
        Int_2D = f.get('/exchange/pixelSum')[()]

        return dict(
            Iq=Iq,
            I_partial=I_partial,
            ql_sta=ql_sta,
            ql_dyn=ql_dyn,
            t0=t0,
            t_el=t_el,
            g2=g2,
            g2_err=g2_err,
            Int_2D=Int_2D,
        )
