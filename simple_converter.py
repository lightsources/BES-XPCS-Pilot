import sys

from creator.nx_creator_xpcs import NXCreator
from loader.nx_loader_aps import APSLoader
from loader.nx_loader_nslsii import NSLSLoader

"""
usage: python simple_converter.py inputfile outputfile loader_id
"""


# TODO add logging and other stuff if desired
# TODO add option to pass input in prompt if not given as sys args
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
        help="NXxpcs (input) data file name",
    )
    parser.add_argument(
        "NeXus_file",
        action="store",
        help="NXxpcs (output) data file name",
    )

    parser.add_argument(
        "Loader_id",
        action="store",
        help="Loader ID defines Loader type",
    )

    # If this flag isn't present, use_q_values defaults to False
    parser.add_argument(
        "--use_q_values",
        action="store_true",
        help="Use this to use q values for dynamic_q_list instead of index values",
    )
    return parser.parse_args()


options = get_user_parameters()
output_filename = options.NeXus_file

input_filename = options.Input_file
loader_id = options.Loader_id
use_q_values = options.use_q_values
# TODO add logic to select loader based on file suffix/user input
# TODO: add additional keyword arguments to have standard signature
if loader_id.lower() == "aps":
    loader = APSLoader(input_file=input_filename)
elif loader_id.lower() == "nslsii":
    # TODO: handle use_q_values in parser
    loader = NSLSLoader(input_file=input_filename, use_q_values=use_q_values)

### GETTING THE DATA IS FLEXIBLE --> Choose best way depedning on data
# Get data dictionaries from selected loader
md_xpcs = loader.xpcs_md()
md_saxs1d = loader.saxs1d_md()
md_saxs2d = loader.saxs2d_md()
md_instrument = loader.instrument_md()


### Instanciate Creator Class
creator = NXCreator(output_filename)

# TODO what to do if file exists (and is still opened elsewhere)? Append?
creator.init_file()
creator.create_entry_group()
creator.create_xpcs_group(
                          g2=md_xpcs.get('g2'),
                          g2_unit=md_xpcs.get('g2_unit'),
                          g2_stderr=md_xpcs.get('g2_stderr'),
                          g2_stderr_unit=md_xpcs.get('g2_stderr_unit'),
                          g2_partials_twotime=md_xpcs.get('g2_partials_twotime'),
                          g2_partials_twotime_unit=md_xpcs.get('g2_partials_twotime_unit'),
                          g2_twotime=md_xpcs.get('g2_twotime'),
                          g2_twotime_unit=md_xpcs.get('g2_twotime_unit'),
                          # TODO find a better name for this entry: e.g. twotime_corr, twotime, C2T_all...?
                          twotime=md_xpcs.get('twotime'),
                          twotime_unit=md_xpcs.get('twotime_unit'),
                          tau=md_xpcs.get('tau'),
                          tau_unit=md_xpcs.get('tau_unit'),
                          mask=md_xpcs.get('mask'),
                          dynamic_roi_map=md_xpcs.get('dynamic_roi_map'),
                          dynamic_q_list=md_xpcs.get('dynamic_q_list'),
                          dynamic_phi_list=md_xpcs.get('dynamic_phi_list'),
                          sqmap=md_xpcs.get('sqmap')
                          )
creator.create_saxs_1d_group(
                             I=md_saxs1d.get("I"),
                             I_unit=md_saxs1d.get("I_unit"),
                             Q=md_saxs1d.get("Q"),
                             Q_unit=md_saxs1d.get("Q_unit"),
                             I_partial=md_saxs1d.get("I_partial"),
                             I_partial_unit=md_saxs1d.get("I_partial_unit"))
creator.create_saxs_2d_group(I=md_saxs2d.get("I"))
creator.create_instrument_group(
                                count_time=md_instrument.get("count_time"),
                                count_time_unit=md_instrument.get("count_time_unit"),
                                frame_time=md_instrument.get("frame_time"),
                                frame_time_unit=md_instrument.get("frame_time_unit"),
                                description=md_instrument.get("description"),
                                distance=md_instrument.get("distance"),
                                distance_unit=md_instrument.get("distance_unit"),
                                x_pixel_size=md_instrument.get("x_pixel_size"),
                                x_pixel_size_unit=md_instrument.get("x_pixel_size_unit"),
                                y_pixel_size=md_instrument.get("y_pixel_size"),
                                y_pixel_size_unit=md_instrument.get("y_pixel_size_unit"),
                                energy=md_instrument.get("energy"),
                                energy_unit=md_instrument.get("energy_unit"))


