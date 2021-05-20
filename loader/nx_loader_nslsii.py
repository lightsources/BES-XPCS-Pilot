import h5py


class NSLSLoader:
    def __init__(self, input_file, use_q_values=True):
        self.data_file = h5py.File(input_file, "r")
        self.use_q_values = use_q_values  # use q values or indices for dqlist

    def get_entry_data(self):
        entry_data = {}
        entry_data['experiment_description'] = self.data_file.get('md').attrs['Measurement']
        entry_data['title'] = self.data_file.get('md').attrs['sample']
        entry_data['entry_identifier'] = self.data_file.get('md').attrs['suid']
        entry_data['entry_identifier_uuid'] = self.data_file.get('md').attrs['uid']
        entry_data['scan_number'] = self.data_file.get('md').attrs['scan_id']
        entry_data['start_time'] = self.data_file.get('md').attrs['start_time']
        entry_data['end_time'] = self.data_file.get('md').attrs['stop_time']
        return entry_data

    def xpcs_md(self):
        xpcs_data = {}
        xpcs_data['frameSum'] = self.data_file.get('imgsum')
        xpcs_data['frameSum_units'] = 'a.u'
        xpcs_data['g2'] = self.data_file.get('g2')
        xpcs_data['g2_units'] = 'a.u'
        xpcs_data['g2_stderr'] = self.data_file.get('g2_stderr')
        xpcs_data['tau'] = self.data_file.get('taus')
        xpcs_data['tau_units'] = 's'
        # TODO: C2 or twotime?
        xpcs_data['twotime'] = self.data_file.get('g12b')
        xpcs_data['twotime_units'] = 'a.u'
        xpcs_data['g2_twotime'] = self.data_file.get('g2_twotime')
        xpcs_data['g2_twotime_units'] = 'a.u'
        xpcs_data['g2_partials_twotime'] = self.data_file.get('g2_partials_twotime')
        xpcs_data['g2_partials_twotime_units'] = 'a.u'

        xpcs_data['mask'] = self.data_file.get('mask')

        xpcs_data['dqmap'] = self.data_file.get('roi_mask')

        # Option to let user pick between q value
        # or q index for dqlist
        d = {int(k): v for k, v in self.data_file.get('qval_dict').attrs.items()}
        q_vals = [d[i][0] for i in sorted(d.keys())]
        if self.use_q_values:
            xpcs_data['dqlist'] = q_vals
            xpcs_data['dqlist_units'] = '1/angstrom'
        else:
            q_index_list = [i + 1 for i in range(len(q_vals))]
            # This is an integer pointer; doesn't need units
            xpcs_data['dqlist'] = q_index_list

        # Angle measurement
        xpcs_data['dphi'] = self.data_file.get('dphi')

        xpcs_data['sqmap'] = self.data_file.get('sqmap')

        return xpcs_data

    def saxs1d_md(self):
        saxs_1d_data = {}
        saxs_1d_data['I'] = self.data_file.get('iq_saxs')
        saxs_1d_data['I_units'] = 'a.u'
        saxs_1d_data['Q'] = self.data_file.get('q_saxs')
        saxs_1d_data['Q_units'] = '1/angstrom'
        saxs_1d_data['I_partial'] = self.data_file.get('I_partial')
        saxs_1d_data['I_partial_units'] = 'a.u'
        return saxs_1d_data

    def saxs2d_md(self):
        saxs_2d_data = {}
        saxs_2d_data['I'] = self.data_file.get('avg_img')
        saxs_2d_data['I_units'] = 'a.u'
        return saxs_2d_data

    def instrument_md(self):
        instrument_data = {}
        #TODO add instrument name e.g. as input when running the converter
        instrument_data['energy'] = self.data_file.get('md').attrs['eiger4m_single_photon_energy']
        instrument_data['energy_units'] = 'eV'
        instrument_data['description'] = self.data_file.get('md').attrs['detector']
        instrument_data['distance'] = self.data_file.get('md').attrs['detector_distance']
        instrument_data['distance_units'] = 'm'
        instrument_data['count_time'] = self.data_file.get('md').attrs['count_time']
        instrument_data['count_time_units'] = 'ms'
        instrument_data['frame_time'] = self.data_file.get('md').attrs['frame_time']
        instrument_data['frame_time_units'] = 'ms'
        instrument_data['beam_center_x'] = self.data_file.get('md').attrs['beam_center_x']
        instrument_data['beam_center_x_units'] = 'pixel'
        instrument_data['beam_center_y'] = self.data_file.get('md').attrs['beam_center_y']
        instrument_data['beam_center_y_units'] = 'pixel'
        instrument_data['x_pixel_size'] = self.data_file.get('md').attrs['x_pixel_size']
        instrument_data['y_pixel_size'] = self.data_file.get('md').attrs['y_pixel_size']
        instrument_data['pixel_size_units'] = 'um'
        return instrument_data
