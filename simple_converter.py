import h5py
from creator.nx_creator_xpcs import NXCreator
from creator.nx_loader_aps import APSLoader
import sys

#TODO add logging and other stuff if desired

#TODO add option to pass input in prompt if not given as sys args
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
        "Loader_id",
        action="store",
        help="Loader ID defines Loader type",
    )
    return parser.parse_args()


options = get_user_parameters()
output_filename = options.NeXus_file
output_file = h5py.File(output_filename, "w")
input_filename = options.Input_file
loader_id = options.Loader_id

#TODO add logic to select loader based on file suffix/user input
if loader_id == "aps" or "APS":
    loader = APSLoader(input_file=input_filename)
elif loader_id == "csx" or "CSX":
    pass
    # loader = CSXLoader(input_file=input_filename)

# Get data dictionaries from selected loader
md_xpcs = loader.xpcs_md()
md_saxs1d = loader.saxs1d_md()
md_saxs2d = loader.saxs2d_md()
md_instrument = loader.instrument_md()

creator = NXCreator(output_file)
group = creator.create_entry_group(experiment_description="XPCS experiment",
                                   title="XPCS")
# NOTE: get() return None if key doesn't exist, None is caught in creator methods
creator.create_xpcs_group(group,
                          g2=md_xpcs.get('g2'),
                          g2_stderr=md_xpcs.get('g2_stderr'),
                          g2_partials_twotime=md_xpcs.get('g2_partials_twotime'),
                          g2_twotime=md_xpcs.get('g2_twotime'),
                          twotime=md_xpcs.get('twotime'),
                          tau=md_xpcs.get('tau'),
                          mask=md_xpcs.get('mask'),
                          dqmap=md_xpcs.get('dqmap'),
                          dqlist=md_xpcs.get('dqlist'),
                          dphilist=md_xpcs.get('dphilist'),
                          sqmap=md_xpcs.get('sqmap')
                          )
creator.create_saxs_1d_group(group,
                             I=md_saxs1d.get("I"),
                             I_partial=md_saxs1d.get("I_partial"))
creator.create_saxs_2d_group(group,
                             I=md_saxs2d.get("I"))
creator.create_instrument_group(group,
                                count_time=md_instrument.get("count_time"),
                                frame_time=md_instrument.get("frame_time"),
                                description=md_instrument.get("description"),
                                distance=md_instrument.get("distance"),
                                x_pixel_size=md_instrument.get("x_pixel_size"),
                                y_pixel_size=md_instrument.get("y_pixel_size"),
                                energy=md_instrument.get("energy"))

output_file.close()