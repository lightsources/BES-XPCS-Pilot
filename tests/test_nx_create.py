import h5py
from creator.nx_creator_xpcs import NXCreator


def test_nx_xpcs(tmp_path):
    with h5py.File(tmp_path / 'test2.hdf5', 'w') as file:
        try:
            creator = NXCreator(file)
            group = creator.create_entry_group(md=md)
            # creator.create_instrument_group(group, instrument_md)
            creator.create_xpcs_group(group, xpcs_md)
            # creator.create_saxs_1d_group(group, saxs_1d_md)
            # creator.create_saxs_2d_group(group, saxs_1d_md)
        except Exception as e:
            raise e
        file.close()

    print(file.name)
    with h5py.File(tmp_path / 'test2.hdf5', 'r') as file:
        assert '/entry/XPCS/name' in file
        # assert file['/entry/instrument/name'][()] == "beamline"
    file.close()


xpcs_md = {"data":
               {"g2": "g2_value",
                "g2_stderr": "g2_stderr_value",
                "tau": "tau_value"
                },
           "twotime":
               {"g2_partials_twotime": "g2_partials_twotime_values",
                "g2_twotime": "g2_twotime_values",
                #TODO figure out how to access large amount of data
                "C": "C_array"
                },
           # TODO check if instrument level is desired
           "mask":
               {"mask": "mask_value",
                "dqmap": "dqmap_value"
                }
           }

saxs_1d_md = {"SAXS_1D": {"name": "beamline"}}
saxs_2d_md = {"SAXS_1D": {"name": "beamline"}}
instrument_md = {"instrument": {"name": "beamline"}}

md = {"title": "title",
      "experimental_description": "XPCS experiment",
      "XPCS": xpcs_md,
      "SAXS_1D": saxs_1d_md,
      "SAXS_2D": saxs_2d_md,
      "Instrument": instrument_md
      }