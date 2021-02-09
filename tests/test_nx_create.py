import h5py
from creator.nx_creator_xpcs import XPCSCreator

def test_nx_xpcs(tmp_path):
    with  h5py.File(tmp_path / 'test.hdf5', 'w') as file:
        try:
            md = {
                "instrument": {
                    "name": "beamline"

                }
            }

            creator = XPCSCreator(file)
            creator.create_entry_group(md=md)
        except Exception as e:
            raise e

    print(file.name)
    with h5py.File(tmp_path / 'test.hdf5', 'r') as file:
        assert '/entry/instrument/name' in file
        assert file['/entry/instrument/name'].value == "beamline"
    
    