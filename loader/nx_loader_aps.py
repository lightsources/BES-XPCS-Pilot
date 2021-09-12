import h5py
import numpy as np


class APSLoader():
    def __init__(self, input_file):
        self.data_file = h5py.File(input_file, 'r')

    def _get_c2t(self):
        c2t_list = []
        if self.data_file.get("exchange/C2T_all") is not None:
            for key in self.data_file.get("exchange/C2T_all"):
                c2t_list.append(self.data_file.get(f"exchange/C2T_all/{key}")[()])
                print(f"add twotime data {key}")
                # currently using first index as running index for slicing
                # TODO if last index is preferred, add transformation here
            c2t_all = np.asarray(c2t_list)
        else:
            c2t_all = None
        return c2t_all

    #TODO change this to a more general approach for different loaders
    def xpcs_md(self):
        xpcs = dict(
            g2=self.data_file.get("/exchange/norm-0-g2"),
            g2_units='a.u.',
            g2_stderr=self.data_file.get("/exchange/norm-0-stderr"),
            tau=self.data_file.get("/exchange/tau"),
            tau_units='s',
            g2_partials_twotime=self.data_file.get("/exchange/g2partials"),
            g2_partials_twotime_units='a.u.',
            g2_twotime=self.data_file.get("/exchange/g2full"),
            g2_twotime_units='a.u.',
            baseline_reference=1,
            # TODO figure out how to access large amount of data
            twotime=self._get_c2t(),
            twotime_units='a.u.',
            mask=self.data_file.get("/xpcs/mask"),
            dqmap=self.data_file.get("/xpcs/dqmap"),
            dqlist=self.data_file.get("/xpcs/dqlist"),
            dphilist=self.data_file.get("/xpcs/dphilist"),
            sqmap=self.data_file.get("/xpcs/sqmap"),
            # sqlist=self.data_file.get("/xpcs/sqlist"),
            sphilist=self.data_file.get("/xpcs/sphilist")
        )
        return xpcs

    def saxs1d_md(self):
        saxs1d = dict(
            I=self.data_file.get("/exchange/partition-mean-total"),
            I_units='a.u.',
            Q=self.data_file.get("/xpcs/sqlist"),
            Q_units= '1/angstrom',
            I_partial=self.data_file.get("/exchange/partition-mean-partial"),
            I_partial_units='a.u.'
        )
        return saxs1d

    def saxs2d_md(self):
        saxs2d = dict(
            I=self.data_file.get("/exchange/pixelSum"),
            I_units='a.u.'
        )
        return saxs2d

    def instrument_md(self):
        instrument = dict(
        #TODO add instrument name e.g. as input when running the converter
            # beam_center_x=self.data_file.get("/measurement/instrument/detector/beam_center"),
            # beam_center_y=self.data_file.get("/measurement/instrument/detector/beam_center"),
            count_time=self.data_file.get("/measurement/instrument/detector/exposure_time"),
            count_time_units='s',
            description=self.data_file.get("/measurement/instrument/detector/manufacturer"),
            distance=self.data_file.get("/measurement/instrument/detector/distance"),
            distance_units='mm',
            energy=self.data_file.get("/measurement/instrument/source_begin/energy"),
            energy_units='keV',
            frame_time=self.data_file.get("/measurement/instrument/detector/exposure_period"),
            frame_time_units='s',
            x_pixel_size=self.data_file.get("/measurement/instrument/detector/x_pixel_size"),
            y_pixel_size=self.data_file.get("/measurement/instrument/detector/y_pixel_size"),
            pixel_size_units='um',
            beam_center_x=self.data_file.get('/measurement/instrument/acquisition/beam_center_x'),
            beam_center_x_units='pixel',
            beam_center_y=self.data_file.get('/measurement/instrument/acquisition/beam_center_y'),
            beam_center_y_units='pixel'
        )
        return instrument


