import numpy as np
import h5py

from creator.nx_creator_xpcs import NXCreator


def get_entry_data(file):
    entry_data = {}
    with h5py.File(file, 'r') as f:
        entry_data['experiment_description'] = f['md'].attrs['Measurement']
        entry_data['title'] = f['md'].attrs['sample']
        entry_data['start_time'] = f['md'].attrs['start_time']
        entry_data['end_time'] = f['md'].attrs['stop_time']
        # TODO: Is scan_number the scan_id or uid?
        # entry_data['scan_number'] = f['md'].attrs['uid']
        entry_data['scan_number'] = f['md'].attrs['scan_id']
        # entry_data['notes'] = ''
    return entry_data


def get_xpcs_data(file, use_q_value=True):
    xpcs_data = {}
    with h5py.File(file, 'r') as f:
        # TODO: should first column of g2 and first tau be excluded?
        xpcs_data['g2'] = np.squeeze(f['g2'])[()]

        # TODO: Does CHX data have this?
        # xpcs_data['g2_stderr'] = np.squeeze(f[''])[()]

        xpcs_data['tau'] = np.squeeze(f['taus'])[()]
        xpcs_data['tau@units'] = 's'

        # TODO: Does CHX data have these?
        # xpcs_data['g2_from_two_time_corr_func_partials'] = np.squeeze(f[''])[()]
        # xpcs_data['g2_from_two_time_corr_func'] = np.squeeze(f[''])[()]
        # xpcs_data['C_0000X'] = np.squeeze(f[''])[()]

        # NOTE: Swapping 0s and 1s in mask here
        xpcs_mask = np.squeeze(f['mask'])[()]
        xpcs_data['mask'] = np.where(xpcs_mask > 0, 0, 1)
        # xpcs_data['mask'] = np.squeeze(f['mask'])[()]
        xpcs_data['mask@units'] = 'boolean'

        xpcs_data['dqmap'] = np.squeeze(f['roi_mask'])[()]

        # TODO: Figure out what to do about using q-vals or q-index
        d = {int(k): v for k, v in f['qval_dict'].attrs.items()}
        q_vals = [d[i][0] for i in sorted(d.keys())]
        if use_q_value:
            xpcs_data['dqlist'] = q_vals
        else:
            q_index_list = [i + 1 for i in range(len(q_vals))]
            xpcs_data['dqlist'] = q_index_list

        # TODO: Does CHX data have this?
        # xpcs_data['dphilist'] = np.squeeze(f[''])[()]

        # TODO: Does CHX data have this?
        # xpcs_data['sqmap'] = np.squeeze(f[''])[()]

        xpcs_data['frameSum'] = np.squeeze(f['imgsum'])[()]

        # TODO: Does CHX data have this?
        # xpcs_data['geometry'] = np.squeeze(f[''])[()]
    return xpcs_data


def get_saxs_1d_data(file):
    saxs_1d_data = {}
    with h5py.File(file, 'r') as f:
        saxs_1d_data['I'] = np.squeeze(f['iq_saxs'])[()]
        saxs_1d_data['I@units'] = 'arbitrary'
        saxs_1d_data['Q'] = np.squeeze(f['q_saxs'])[()]
        # TODO: Pixel or 1/angstrom for Q units?
        # saxs_1d_data['Q@units'] = 'pixel'
        saxs_1d_data['Q@units'] = '1/angstrom'
        # TODO: Does CHX data have this?
        # saxs_1d_data['I_partial'] = np.squeeze(f[''])[()]
    return saxs_1d_data


def get_saxs_2d_data(file):
    saxs_2d_data = {}
    with h5py.File(file, 'r') as f:
        # TODO: are there units here?
        saxs_2d_data['I'] = np.squeeze(f['avg_img'])[()]
        saxs_2d_data['I@units'] = 'arbitrary'
    return saxs_2d_data


def get_instrument_data(file):
    instrument_data = {}
    with h5py.File(file, 'r') as f:
        instrument_data['count_time'] = f['md'].attrs['count_time']
        instrument_data['count_time@units'] = 'ms'
        instrument_data['frame_time'] = f['md'].attrs['frame_time']
        instrument_data['frame_time@units'] = 'ms'
        instrument_data['description'] = f['md'].attrs['detector']
        instrument_data['distance'] = f['md'].attrs['detector_distance']
        instrument_data['distance@units'] = 'm'
        instrument_data['x_pixel_size'] = f['md'].attrs['x_pixel_size']
        instrument_data['x_pixel_size@units'] = 'um'
        instrument_data['y_pixel_size'] = f['md'].attrs['y_pixel_size']
        instrument_data['y_pixel_size@units'] = 'um'
        instrument_data['energy'] = f['md'].attrs['eiger4m_single_photon_energy']
        instrument_data['energy@units'] = 'eV'
    return instrument_data


def get_sample_data(file):
    sample_data = {}
    # TODO: Nothing here is in CHX...
    # with h5py.File(file, 'r') as f:
    #     print()
    #     sample_data['temperature_set'] = None  # np.squeeze(f[''])[()]
    #     sample_data['temperature'] = None  # np.squeeze(f[''])[()]
    #     sample_data['position_x'] = None  # np.squeeze(f[''])[()]
    #     sample_data['position_y'] = None  # np.squeeze(f[''])[()]
    #     sample_data['position_z'] = None  # np.squeeze(f[''])[()]
    return sample_data


def main():
    # import pprint

    DATAFILE = '/Users/abigailgiles/Downloads/' \
        'uid=c8a1fb1f-1960-49f8-927a-c29fca8aaafa__Res.h5'
    # print(f'{DATAFILE = }')
    NXFILE = 'CHX_nexus.h5'
    print('Reading datafile...')
    entry_data = get_entry_data(DATAFILE)
    # print('\nentry_data:')
    # pprint.pp(entry_data)

    instrument_data = get_instrument_data(DATAFILE)
    # print('\ninstrument_data:')
    # pprint.pp(instrument_data)

    xpcs_data = get_xpcs_data(DATAFILE, use_q_value=True)
    # print('\nxpcs_data:')
    # pprint.pp(xpcs_data)

    saxs_1d_data = get_saxs_1d_data(DATAFILE)
    # print('\nsaxs_1d_data:')
    # pprint.pp(saxs_1d_data)

    saxs_2d_data = get_saxs_2d_data(DATAFILE)
    # print('\nsaxs_2d_data:')
    # pprint.pp(saxs_2d_data)

    print('Now attempting to write nexus file...')
    with h5py.File(NXFILE, 'w') as f:
        creator = NXCreator(f)
        # dictionary method of creating file
        # group = creator.create_entry_group(entry_data)
        # creator.create_xpcs_group(group, xpcs_data)
        # creator.create_instrument_group(group, instrument_data)
        # creator.create_saxs_1d_group(group, saxs_1d_data)
        # creator.create_saxs_2d_group(group, saxs_2d_data)

        # All items are their own parameter
        group = creator.create_entry_group(
            experiment_description=entry_data["experiment_description"],
            title=entry_data["title"],
            start_time=entry_data["start_time"],
            end_time=entry_data["end_time"],
            scan_number=entry_data["scan_number"],
            notes=entry_data["notes"],
        )
        creator.create_xpcs_group(
            h5parent=group,
            g2=xpcs_data["g2"],
            g2_stderr=xpcs_data["g2_stderr"],
            tau=xpcs_data["tau"],
            g2_from_two_time_corr_func_partials=xpcs_data["g2_from_two_time_corr_func_partials"],
            g2_from_two_time_corr_func=xpcs_data["g2_from_two_time_corr_func"],
            C_0000X=xpcs_data["C_0000X"],
            mask=xpcs_data["mask"],
            dqmap=xpcs_data["dqmap"],
            dqlist=xpcs_data["dqlist"],
            dphilist=xpcs_data["dphilist"],
            sqmap=xpcs_data["sqmap"],
            frameSum=xpcs_data["frameSum"],
            geometry=xpcs_data["geometry"],
        )
        creator.create_instrument_group(
            h5parent=group,
            count_time=instrument_data["count_time"],
            frame_time=instrument_data["frame_time"],
            description=instrument_data["description"],
            distance=instrument_data["distance"],
            x_pixel_size=instrument_data["x_pixel_size"],
            y_pixel_size=instrument_data["y_pixel_size"],
            energy=instrument_data["energy"],
        )
        creator.create_saxs_1d_group(
            h5parent=group,
            I=saxs_1d_data["I"],
            Q=saxs_1d_data["Q"],
            I_partial=saxs_1d_data["I_partial"],
        )
        creator.create_saxs_2d_group(
            h5parent=group,
            I=saxs_2d_data["I"],
        )


if __name__ == '__main__':
    main()
