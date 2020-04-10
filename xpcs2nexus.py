#!/usr/bin/env python

"""
Write a NeXus file from the XPCS data
"""

import logging
import os

import loaders
import nxwriter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def q_based_mask_names(q_array):
    """
    Create a text name of each mask from its Q value

    Write each Q value to 2 significant figures,
    using fixed-point notation, no trailing zeros

    Result should be a string that h5py can write 
    in a string array as a dataset, thus it must 
    be byte-encoded.
    """
    def formatter(value):
        s_value = f"{value:.2e}"        # 2 sig figs
        s_value = f"Q={float(s_value)}"   # fixed-point
        return s_value.encode()         # byte-encode

    return list(map(formatter, q_array))


def q_ranges_from_roi_array(q_array: np.ndarray) -> List[Tuple[float]]:
    """
    Takes a labeled roi array composed of many q-ring rois and extracts each roi's range.

    Parameters
    ----------
    q_array : np.ndarray
        A labeled roi array composed of many q-ring rois

    Returns
    -------
    List[Tuple[float]]
        The range of each ring roi.

    """

    unique_levels = np.unique(q_array)
    return list(zip(unique_levels, unique_levels[1:]))


def q_ring_roi(q_min, q_max):
    return {"type": "q Ring ROI",
            "q_min": q_min,
            "q_max": q_max}


def process_data_file(data_file, nx_file=None):
    """
    read the QMap file, make plots, write the NeXus file
    """
    if data_file.endswith(nxwriter.NX_EXTENSION):
        raise ValueError(
            f"Data file must not end with '{nxwriter.NX_EXTENSION}'")

    nx_file = nx_file or os.path.splitext(data_file)[0] + nxwriter.NX_EXTENSION

    path = os.path.dirname(__file__)
    logger.debug("data file path: %s", path)
    data_file = os.path.abspath(os.path.join(path, data_file))
    logger.debug("data file path: %s", data_file)

    # read the Qmap
    qmap = loaders.read_qmap(data_file)

    # read the metadata
    md = loaders.read_metadata(data_file)
    logger.debug("metadata: %s", str(md))

    # read the XPCS data (results)
    xpcs = loaders.read_xpcs_results(data_file)
    logger.debug("XPCS data keys: %s", str(xpcs.keys()))

    mask, mask_names = loaders.compute_mask(qmap)

    # replace the generic names with Q-based names
    mask_names = q_based_mask_names(xpcs["ql_dyn"])

    # build procedural roi's
    # TODO: its only a bit silly to have to regenerate the q-ring-rois' procedural form, when they are constructed
    #       procedurally, but it illustrates the NeXus structure. Consider changing this upstream later.
    rois = map(lambda q_range: q_ring_roi(*q_range), q_ranges_from_roi_array(xpcs["ql_dyn"]))

    logger.debug(
        "mask names: %s", 
        str([s.decode() for s in mask_names]))

    nxwriter.write_nx_file(nx_file, xpcs, qmap, mask, mask_names, rois, md)


if __name__ == "__main__":
    process_data_file(loaders.DATAFILE)
