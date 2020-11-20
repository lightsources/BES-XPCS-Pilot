import datetime

import numpy as np
import h5py


def write_nx_file(nx_file, data, masks, xpcs, q, q_ind,
                  md, others, use_q_ind=True):
    # use_q_ind tells whether to use q index values (default)
    #     or actual q values
    with h5py.File(nx_file, 'w') as nx:
        write_file_header(nx)

        # entry group
        nxentry = create_entry_group(nx, data)

        # instrument group
        create_instrument_group(nxentry, data)

        # sample group
        create_sample_group(nxentry, data)

        # SAXS_1D group
        create_SAXS_1D_group(nxentry, xpcs)

        # SAXS_2D group
        create_SAXS_2D_group(nxentry, xpcs, masks)

        # XPCS group
        create_XPCS_group(nxentry, xpcs, masks, q, q_ind, use_q_ind)

        # metadata group
        create_metadata_group(nxentry, md, others)


def write_file_header(h5parent):
    timestamp = datetime.datetime.now().isoformat(sep=' ', timespec='seconds')
    h5parent.attrs['default'] = 'entry'
    h5parent.attrs['file_name'] = h5parent.filename
    h5parent.attrs['file_time'] = timestamp
    h5parent.attrs['instrument'] = 'CHX XPCS'
    h5parent.attrs['creator'] = __file__
    h5parent.attrs['HDF5_Version'] = h5py.version.hdf5_version
    h5parent.attrs['h5py_version'] = h5py.version.version


def create_entry_group(h5parent, data):
    nxentry = h5parent.create_group('entry')
    nxentry.attrs['NX_class'] = 'NXentry'

    def to_iso(timestring):
        format = "%Y-%m-%d %H:%M:%S"  # 2020-10-23 13:30:30
        try:
            dt = datetime.datetime.strptime(timestring, format)
            return dt.isoformat()
        except ValueError:
            raise ValueError(f"could not parse date/time string: {timestring}")

    ds = nxentry.create_dataset('title', data=data['Measurement'])
    ds.attrs['target'] = ds.name
    ds = nxentry.create_dataset('start_time', data=to_iso(data['start_time']))
    ds.attrs['target'] = ds.name
    ds = nxentry.create_dataset('end_time', data=to_iso(data['stop_time']))
    ds.attrs['target'] = ds.name
    ds = nxentry.create_dataset('run_cycle', data=data['cycle'])
    ds.attrs['target'] = ds.name
    ds = nxentry.create_dataset('entry_identifier', data=data['uid'])
    ds.attrs['target'] = ds.name
    ds = nxentry.create_dataset('scan_number', data=data['scan_id'])
    ds.attrs['target'] = ds.name

    h5parent.attrs['default'] = nxentry.name.split('/')[-1]
    return nxentry


def create_instrument_group(h5parent, data):
    nxinstrument = h5parent.create_group('instrument')
    nxinstrument.attrs['NX_class'] = 'NXinstrument'
    nxinstrument.attrs['canSAS_class'] = 'SASinstrument'
    nxinstrument.attrs['target'] = nxinstrument.name
    ds = nxinstrument.create_dataset('name', data='CHX XPCS')
    ds.attrs['short_name'] = 'XPCS'

    nxsource = nxinstrument.create_group('source')
    nxsource.attrs['NX_class'] = 'NXsource'
    nxsource.attrs['canSAS_class'] = 'SASsource'
    nxsource.attrs['target'] = nxsource.name
    ds = nxsource.create_dataset('name',
                                 data='National Synchrotron Light Source II')
    ds.attrs['short_name'] = 'NSLS-II'
    ds = nxsource.create_dataset('type', data='Synchrotron X-ray Source')
    ds.attrs['target'] = ds.name
    nxsource.create_dataset('probe', data='x-ray')

    # using NXmonochromator here (NXbeam?)
    nxmono = nxinstrument.create_group('monochromator')
    nxmono.attrs['NX_class'] = 'NXmonochromator'
    ds = nxmono.create_dataset('energy',
                               data=data['eiger4m_single_photon_energy'])
    ds.attrs['units'] = 'eV'
    ds.attrs['target'] = ds.name
    ds = nxmono.create_dataset('wavelength',
                               data=data['eiger4m_single_wavelength'])
    ds.attrs['units'] = 'angstrom'
    ds.attrs['target'] = ds.name

    nxsource['radiation'] = nxsource['type']

    wavelength = nxsource['/entry/instrument/monochromator/wavelength']
    nxsource['incident_wavelength'] = wavelength

    # detector group
    create_detector_group(nxinstrument, data)

    return nxinstrument


def create_detector_group(h5parent, data):
    nxdet = h5parent.create_group('detector')
    nxdet.attrs['NX_class'] = 'NXdetector'
    ds = nxdet.create_dataset('distance', data=data['detector_distance'])
    ds.attrs['units'] = 'm'
    ds.attrs['target'] = ds.name
    ds = nxdet.create_dataset('x_pixel_size', data=data['x_pixel_size'])
    ds.attrs['units'] = 'um'
    ds.attrs['target'] = ds.name
    ds = nxdet.create_dataset('y_pixel_size', data=data['y_pixel_size'])
    ds.attrs['units'] = 'um'
    ds.attrs['target'] = ds.name
    ds = nxdet.create_dataset('beam_center_x',
                              data=data['eiger4m_single_beam_center_x'])
    ds.attrs['units'] = 'pixels'
    ds.attrs['target'] = ds.name
    ds = nxdet.create_dataset('beam_center_y',
                              data=data['eiger4m_single_beam_center_y'])
    ds.attrs['units'] = 'pixels'
    ds.attrs['target'] = ds.name
    ds = nxdet.create_dataset('count_time', data=data['count_time'])
    ds.attrs['units'] = 's'
    ds.attrs['target'] = ds.name
    ds = nxdet.create_dataset('frame_time', data=data['frame_time'])
    ds.attrs['units'] = 's'
    ds.attrs['target'] = ds.name
    nxdet.create_dataset('description', data=data['detector'])
    return nxdet


def create_sample_group(h5parent, data):
    nxsample = h5parent.create_group('sample')
    nxsample.attrs['NX_class'] = 'NXsample'
    nxsample['target'] = nxsample.name
    nxsample['name'] = data['sample']
    return nxsample


def create_SAXS_1D_group(h5parent, xpcs):
    group = h5parent.create_group('SAXS_1D')
    group.attrs['NX_class'] = 'NXsubentry'
    group.attrs['canSAS_class'] = 'SASentry'
    group.attrs['version'] = '1.1'
    group.create_dataset('definition', data='NXcanSAS')

    group['run'] = group['/entry/title']
    group.create_dataset('title', data='1D SAXS from XPCS data')

    group.attrs['default'] = 'data'
    nxdata = group.create_group('data')
    nxdata.attrs['NX_class'] = 'NXdata'
    nxdata.attrs['canSAS_class'] = 'SASdata'
    nxdata.attrs['signal'] = 'I'
    nxdata.attrs['I_axes'] = 'Q'
    nxdata.attrs['Q_indices'] = 0

    signal = nxdata.create_dataset(
        'I',
        data=xpcs['iq_saxs'],
        compression='gzip',
        compression_opts=9)
    signal.attrs['units'] = 'arbitrary'
    # signal.attrs['units_details'] = ''
    ds = nxdata.create_dataset(
        'Q',
        data=xpcs['q_saxs'],
        compression='gzip',
        compression_opts=9)
    ds.attrs['units'] = '1/angstrom'  # TODO: is this right?

    group['instrument'] = group['/entry/instrument']
    group['sample'] = group['/entry/sample']

    return group


def create_SAXS_2D_group(h5parent, xpcs, masks):
    # using masks['mask'], looks like it goes with avg_img
    group = h5parent.create_group('SAXS_2D')
    group.attrs['NX_class'] = 'NXsubentry'
    group.attrs['canSAS_class'] = 'SASentry'
    group.attrs['version'] = '1.1'
    group.create_dataset('definition', data='NXcanSAS')

    group['run'] = group['/entry/title']
    group.create_dataset('title', data='2D SAXS from XPCS data')

    group.attrs['default'] = 'data'
    nxdata = group.create_group('data')
    nxdata.attrs['NX_class'] = 'NXdata'
    nxdata.attrs['canSAS_class'] = 'SASdata'
    nxdata.attrs['signal'] = 'I'
    # nxdata.attrs['I_axes'] = 'Q'
    # nxdata.attrs['Q_indices'] = 0

    ds = nxdata.create_dataset(
        'I',
        data=xpcs['avg_img'],
        compression='gzip',
        compression_opts=9)
    ds.attrs['units'] = 'arbitrary'
    # signal.attrs['units_details'] = ''

    # TODO: Q?
    # ds = nxdata.create_dataset(
    #     'Q',
    #     data='?',
    #     compression='gzip',
    #     compression_opts=9)
    # ds.attrs['units'] = ''

    nxdata.attrs['mask'] = 'mask'

    # TODO: which mask here?
    # roi_mask = dqmap
    # mask = more of a pixel_mask that looks like it goes with avg_img
    # saxs_mask = np.where(masks['roi_mask'] > 0, 0, 1)
    saxs_mask = np.where(masks['mask'] > 0, 0, 1)
    ds = nxdata.create_dataset(
        'mask',
        data=saxs_mask,
        compression='gzip',
        compression_opts=9)
    ds.attrs['units'] = 'boolean'

    group['instrument'] = group['/entry/instrument']
    group['sample'] = group['/entry/sample']

    return group


def create_XPCS_group(h5parent, xpcs, masks, q, q_ind, use_q_ind):
    group = h5parent.create_group('XPCS')
    group.attrs['NX_class'] = 'NXprocess'
    group['title'] = group['/entry/title']
    group.create_dataset('experiment_description', data='XPCS results')

    nxdata = group.create_group('data')
    nxdata.attrs['NX_class'] = 'NXdata'
    nxdata.attrs['target'] = nxdata.name
    group.attrs['default'] = 'data'

    nxdata.attrs['signal'] = 'g2'
    nxdata.attrs['axes'] = 'tau', 'q'
    signal = nxdata.create_dataset(
        'g2',
        data=xpcs['g2'][1:],
        compression='gzip',
        compression_opts=9)
    signal.attrs['units'] = 'scale'
    signal.attrs['long_name'] = 'XPCS g2(t, Q)'
    signal.attrs['target'] = signal.name
    ds = nxdata.create_dataset(
        'tau',
        data=xpcs['taus'][1:],
        compression='gzip',
        compression_opts=9)
    ds.attrs['units'] = 's'
    if use_q_ind:
        # using q index values here
        ds = nxdata.create_dataset(
            'q_ind',
            data=q_ind,
            compression='gzip',
            compression_opts=9)
    else:
        # using q vals here
        ds = nxdata.create_dataset(
            'q',
            data=q,
            compression='gzip',
            compression_opts=9)
        ds.attrs['units'] = '1/angstrom'

    nxdata.create_dataset(
        'frameSum',
        data=xpcs['imgsum'],
        compression='gzip',
        compression_opts=9)

    group['instrument'] = group['/entry/instrument']
    group['sample'] = group['/entry/sample']

    # mask group
    # create_mask_group(group['instrument'], masks, q, q_ind, use_q_ind)
    create_mask_group(nxdata, masks, q, q_ind, use_q_ind)

    # roi group
    # create_roi_group(group['instrument'], q_ind)
    create_roi_group(nxdata, q_ind)

    return group


def create_mask_group(h5parent, masks, q, q_ind, use_q_ind):
    # mask = roi_mask but with actual q vals? Maybe don't have
    # dqmap = roi_mask
    # dqlist = q or q_ind
    nxmask = h5parent.create_group('mask')
    nxmask.attrs['NX_class'] = 'NXarraymask'
    nxmask.create_dataset('usage', data='Selective')
    nxmask.create_dataset('dqmap',
                          data=masks['roi_mask'],
                          compression='gzip',
                          compression_opts=5)
    if use_q_ind:
        # q_ind = q index value
        nxmask.create_dataset('dqlist', data=q_ind)
    else:
        # q = actual q vals
        nxmask.create_dataset('dqlist', data=q)

    return nxmask


def create_roi_group(h5parent, q_ind):
    group = h5parent.create_group('rois')
    group.attrs['NX_class'] = 'NXnote'
    for i in q_ind:
        roi_group = group.create_group(f'roi_{i}')
        roi_group.attrs['NX_class'] = 'NXparameterizedmask'
        roi_group.attrs['usage'] = 'Selective'
    return group


def create_metadata_group(h5parent, md, others):
    nxnote = h5parent.create_group('metadata')
    nxnote.attrs['NX_class'] = 'NXnote'
    for k, v in md.items():
        nxnote.create_dataset(k, data=v)

    # for k, v in others.items():
    #     nxnote.create_dataset(k, data=v)

    return nxnote
