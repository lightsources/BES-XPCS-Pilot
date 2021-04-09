import nsls_loaders
import nsls_filewriter

# NOTE: need full path to hdf file
DATAFILE = "uid=c8a1fb1f-1960-49f8-927a-c29fca8aaafa__Res.h5"
NEXUSFILE = 'CHX_NeXus_file.nxs'


if __name__ == '__main__':
    print("Reading hdf5 file")
    data = nsls_loaders.read_metadata(DATAFILE)
    masks = nsls_loaders.get_masks(DATAFILE)
    xpcs = nsls_loaders.read_xpcs_data(DATAFILE)
    q, q_ind = nsls_loaders.get_roi_q_vals(DATAFILE)
    # others holds the things I don't know what to do with yet
    md, others = nsls_loaders.read_other_data(DATAFILE)

    print('Writing NeXus file')
    nsls_filewriter.write_nx_file(NEXUSFILE, data, masks,
                                  xpcs, q, q_ind, md, others,
                                  use_q_ind=True)
    print('Done')


def convert_hdf_to_nexus(hdffile, nexusfile):
    print("Reading hdf5 file")
    data = nsls_loaders.read_metadata(hdffile)
    masks = nsls_loaders.get_masks(hdffile)
    xpcs = nsls_loaders.read_xpcs_data(hdffile)
    q, q_ind = nsls_loaders.get_roi_q_vals(hdffile)
    # others holds the things I don't know what to do with yet
    md, others = nsls_loaders.read_other_data(hdffile)

    print('Writing NeXus file')
    nsls_filewriter.write_nx_file(nexusfile, data, masks,
                                  xpcs, q, q_ind, md, others,
                                  use_q_ind=True)
    print('Done')
