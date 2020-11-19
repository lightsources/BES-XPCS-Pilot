import numpy as np
import h5py


def read_metadata(filename):
    data = {}

    data_keys = ['Measurement',
                 'sample',
                 'count_time',
                 'detector',
                 'detector_distance',
                 'frame_time',
                 'start_time',
                 'stop_time',
                 'uid',
                 'scan_id',
                 'x_pixel_size',
                 'y_pixel_size',
                 'eiger4m_single_beam_center_x',
                 'eiger4m_single_beam_center_y',
                 'eiger4m_single_photon_energy',
                 'eiger4m_single_wavelength',
                 'cycle',
                 ]

    with h5py.File(filename, 'r') as file:
        data['file_name'] = filename
        for k in data_keys:
            data[k] = file['md'].attrs[k]

    return data


def get_masks(filename):
    all_masks = {}
    with h5py.File(filename, 'r') as file:
        for k in ['pixel_mask',
                  'mask',
                  'roi_mask',
                  ]:
            all_masks[k] = np.squeeze(file[k])[()]
    return all_masks


def read_xpcs_data(filename):
    xpcs = {}
    data_keys = ['iq_saxs',
                 'q_saxs',
                 'avg_img',
                 'imgsum',
                 'taus',
                 'g2',
                 ]
    with h5py.File(filename, 'r') as file:
        for k in data_keys:
            xpcs[k] = np.squeeze(file[k])[()]
    return xpcs


def get_roi_q_vals(filename):
    with h5py.File(filename, 'r') as file:
        d = {int(k): v for k, v in file['qval_dict'].attrs.items()}
        q_vals = [d[i][0] for i in sorted(d.keys())]
    q_index_list = [i + 1 for i in range(len(q_vals))]
    return q_vals, q_index_list  # /entry/xpcs/data/dqlist


def read_other_data(filename):
    """
    This is for the stuff I'm not sure what to do with yet
    """
    md = {}
    others = {}

    other_md_keys = ['beamline_id',
                     'number of images',
                     'framerate',
                     'owner',
                     'plan_name',
                     'plan_type',
                     'data path',
                     'eiger4m_single_threshold_energy',
                     'mask_file',
                     'metadata_file',
                     'roi_mask_file',
                     'shutter_mode',
                     'suid',
                     'user'
                     ]

    data_keys = ['bad_frame_list',
                 'g12b',
                 'g2b',
                 'iqst',
                 'mean_int_sets',
                 'qt',
                 'tausb',
                 'times_roi',
                 ]

    fit_keys = ['g2_fit_paras',
                'g2b_fit_paras',
                ]

    with h5py.File(filename, 'r') as file:
        for k in other_md_keys:
            md[k] = file['md'].attrs[k]

        for k in data_keys:
            others[k] = np.squeeze(file[k])[()]

        for k in fit_keys:
            k_name = k.split('_')[0]
            for i in file[k]:
                others[f'{k_name}_{i}'] = np.squeeze(file[k][i])[()]

    return md, others
