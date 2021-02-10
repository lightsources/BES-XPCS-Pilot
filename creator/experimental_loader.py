from .nx_creator_xpcs import NXCreator

class Loader():
    """This is a non-working class added simply to demonstrate an idea.
    The NXCreator has methods that take as input a dict of fields with their data.
    This could potentially be a memory problem with large datasets. What if it
    took the dict (without data) and a generator for the data? The a Loader
    like this could send that generator as a parameter and write out chunks to be read.
    Heck, maybe instead of an input 
    """
    def __init__(self, nxcreator: NXCreator):
        self._creator = nxcreator

    def go():
        # now lets do the stuff
        # first, gather top level data
        top_dict = {}

        self._creator.create_entry_group(top_dict)

        # SAX1d
        def generate_sax_data():
            foo = []
            yield foo

        saxs_1d_md = {"SAXS_1D": 
                        {
                            "name": "beamline",
                            "some_data": generate_sax_data
                        }               
                    }

        self._creator.create_saxs_1d_group(saxs_1d_md)