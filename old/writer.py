#!/usr/bin/env python

"""

write XPCS results as a NeXus data file given a DataExchange results file

see: https://github.com/aps-8id-dys/ipython-8idiuser/issues/176

test file: /net/wolf/data/xpcs8/2020-2/comm202006/cluster_results/F020_D100_att02_35p00C_0002_0001-100000.hdf
"""

import argparse
import logging
import os
import sys
import xpcs2nexus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_options():
    cwd = os.getcwd()

    parser = argparse.ArgumentParser(
        prog=os.path.split(sys.argv[0])[-1], 
        description=__doc__.strip().splitlines()[0],
        )

    parser.add_argument(
        'dx_file', 
        type=str, 
        help="XPCS results file (DX format)")

    parser.add_argument(
        '-dir', 
        nargs='?', 
        default=cwd,
        help=f"output file directory, default: current directory ({cwd})")

    parser.add_argument(
        '-nx',
        type=str,
        nargs='?',
        default=".nx",
        help="(output) NeXus file extension, default: .nx")

    return parser.parse_args()


def main():
    options = get_options()
    logger.debug(f"command-line options: {options}")

    if not os.path.exists(options.dx_file):
        raise FileExistsError(f"file does not exist: {options.dx_file}")

    if not os.path.exists(options.dir):
        raise FileExistsError(f"output directory does not exist: {options.dir}")

    ext = options.nx
    if not ext.startswith("."):
        ext = "." + ext

    short_name = os.path.split(options.dx_file)[-1]
    nx_file = os.path.join(options.dir, os.path.splitext(short_name)[0] + ext)

    # check that input and output file names are different
    if os.path.abspath(options.dx_file) == os.path.abspath(nx_file):
        raise ValueError(
            f"Input and output file names are identical ({options.dx_file})."
            "  Will not overwrite the input file."
        )

    xpcs2nexus.process_data_file(options.dx_file, nx_file)


if __name__ == "__main__":
    main()
