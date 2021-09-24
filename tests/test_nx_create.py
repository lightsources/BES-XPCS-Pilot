import h5py
from creator.nx_creator_xpcs import NXCreator


def test_nx_xpcs(tmp_path):
    with h5py.File(tmp_path + '/test2.hdf5', 'w') as file:
        try:
            creator = NXCreator(file)
            group = creator.create_entry_group(md=md)
            # creator.create_instrument_group(group, instrument_md)
            creator.create_xpcs_group(group, xpcs_md)
            # creator.create_saxs_1d_group(group, saxs_1d_md)
            # creator.create_saxs_2d_group(group, saxs_1d_md)
        except Exception as e:
            raise e

    print(file.name)
    with h5py.File(tmp_path + '/test2.hdf5', 'r') as file:
        assert '/entry/XPCS/name' in file
        # assert file['/entry/instrument/name'][()] == "beamline"
    file.close()

#TODO smart way to fill the values of a dict like this in a loader module
#TODO add units
xpcs_md = {"g2": "g2_value",
           "g2_stderr": "g2_stderr_value",
           "tau": "tau_value",
           "g2_partials_twotime": "g2_partials_twotime_values",
           "g2_twotime": "g2_twotime_values",
           #TODO figure out how to access large amount of data
           # "C": "C_shaped_array"
           "mask": "mask_value",
           "dynamic_roi_map": "dynamic_roi_map_value"
            }


saxs_1d_md = {"I": "I_value",
              "I_partial": "I_partial_value"}

saxs_2d_md = {"I": "I_values"}

instrument_md = {"count_time": "count_time_value",
                 "frame_time": "frame_time_value",
                 #...
                 }
#TODO decide if we want a single dict (with sub-dicts) or multiple dicts
# --> modify NXCreator accordingly
md = {"title": "title",
      "experimental_description": "XPCS experiment",
      "XPCS": xpcs_md,
      "SAXS_1D": saxs_1d_md,
      "SAXS_2D": saxs_2d_md,
      "Instrument": instrument_md
      }

