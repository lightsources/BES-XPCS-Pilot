import h5py
from creator.nx_creator_xpcs import NXCreator
from creator.nx_loader_aps import APSLoader
import sys

#TODO add logging and other stuff if desired

def get_user_parameters():
    """configure user's command line parameters from sys.argv"""
    import argparse

    parser = argparse.ArgumentParser(
        prog=sys.argv[0], description="NXcxi_ptycho writer"
    )

    # thanks to: https://stackoverflow.com/a/34065768/1046449
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="logging verbosity",
    )

    parser.add_argument(
        "-V",
        "--version",
        action="version",
        help="print version and exit",
        version="development version",
    )

    # TODO check if this input makes sense
    parser.add_argument(
        "Input_file",
        action="store",
        help="NXcxi_ptycho (input) data file name",
    )
    parser.add_argument(
        "NeXus_file",
        action="store",
        help="NXcxi_ptycho (output) data file name",
    )

    parser.add_argument(
        "loader_id",
        action="store",
        help="Loader ID defines Loader type",
    )
    return parser.parse_args()


options = get_user_parameters()
output_filename = options.NeXus_file
output_file = h5py.File(output_filename, "w")
input_filename = options.Input_file

#TODO remove testing dicts
xpcs_md = {"g2": "g2_value",
           "g2_stderr": "g2_stderr_value",
           "tau": "tau_value",
           "g2_partials_twotime": "g2_partials_twotime_values",
           "g2_twotime": "g2_twotime_values",
           #TODO figure out how to access large amount of data
           # "C": "C_shaped_array"
           "mask": "mask_value",
           "dqmap": "dqmap_value"
            }

md = {"title": "title",
      "experimental_description": "XPCS experiment",
      "XPCS": xpcs_md,
      # "SAXS_1D": saxs_1d_md,
      # "SAXS_2D": saxs_2d_md,
      # "Instrument": instrument_md
      }

creator = NXCreator(output_file)
#TODO add logic to select loader based on file suffix/user input
#TODO catch exceptions if certain fields are not avail in file
aps_loader = APSLoader(input_file=input_filename)
md_xpcs = aps_loader.xpcs_md()
md_saxs1d = aps_loader.saxs1d_md()
md_saxs2d = aps_loader.saxs2d_md()
md_instrument = aps_loader.instrument_md()

group = creator.create_entry_group(md=md)
creator.create_xpcs_group(group, xpcs_md)
# creator.create_xpcs_group(group, md_xpcs)
# creator.create_saxs_1d_group(group, md_saxs1d)
# creator.create_saxs_2d_group(group, md_saxs2d)
# creator.create_instrument_group(group, md_instrument)
