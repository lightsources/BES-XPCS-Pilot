from creator.nx_creator_xpcs import NXCreator
from loader.nx_loader_aps import APSLoader
from loader.nx_loader_nslsii import NSLSLoader

import sys

class Writer():
    """This is a non-working class added simply to demonstrate an idea.
    The NXCreator has methods that take as input a dict of fields with their data.
    This could potentially be a memory problem with large datasets. What if it
    took the dict (without data) and a generator for the data? The a Loader
    like this could send that generator as a parameter and write out chunks to be read.
    Heck, maybe instead of an input 
    """
    def __init__(self, nxcreator: NXCreator):
        self._creator = nxcreator

        options = self.get_user_parameters()
        self.output_filename = options.NeXus_file
        self.input_filename = options.Input_file
        self.loader_id = options.loader_id

    def get_loader(self):
        if self.loader_id == 'aps-8idi':
            loader = APSLoader(input_file=self.input_filename)
        # elif loader_id == 'nsns-ii-chx'
        #     loader = ...
        return loader

    def go(self):
        # now lets do the stuff
        # first, gather top level data
        top_dict = {}
        self._creator.create_entry_group(top_dict)

        loader = self.get_loader()
        xpcs_md = loader.xpcs_md
        self._creator.create_xpcs_group(xpcs_md)

        # self._creator.create_saxs_1d_group(saxs_1d_md)



    # xpcs_md = {"g2": "g2_value",
    #            "g2_stderr": "g2_stderr_value",
    #            "tau": "tau_value",
    #            "g2_partials_twotime": "g2_partials_twotime_values",
    #            "g2_twotime": "g2_twotime_values",
    #            #TODO figure out how to access large amount of data
    #            # "C": "C_shaped_array"
    #            "mask": "mask_value",
    #            "dynamic_roi_map": "dynamic_roi_map_value"
    #         }


    def get_user_parameters(self):
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

        #TODO check if this input makes sense
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




if __name__ == "__main__":
    create = Writer(NXCreator("/"))
    create.go()