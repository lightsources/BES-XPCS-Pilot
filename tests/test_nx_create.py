import h5py
from creator.nx_creator_xpcs import NXCreator

def test_nx_xpcs(tmp_path):
    with  h5py.File(tmp_path / 'test.hdf5', 'w') as file:
        try:
            

            creator = NXCreator(file)
            group = creator.create_entry_group(md=md)

            
            creator.create_instrument_group(group, md=instrument_md)
            creator.create_xpcs_group(group, md=md)
            creator.create_saxs_1d_group(group, md=saxs_1d_md)
            creator.create_saxs_2d_group(group, md=md)
        except Exception as e:
            raise e

    print(file.name)
    with h5py.File(tmp_path / 'test.hdf5', 'r') as file:
        assert '/entry/instrument/name' in file
        assert file['/entry/instrument/name'][()] == "beamline"
    
instrument_md = {"instrument": {"name": "beamline"}}
saxs_1d_md = {"SAXS_1D": {"name": "beamline"}}