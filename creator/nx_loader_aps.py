import h5py


class APSLoader():

    def __init__(self, input_file):
        self.data_file = h5py.File[input_file, 'r']

    #TODO move these to a more general approach for different loaders
    def xpcs_md(self):
        xpcs = dict(
            g2=self.data_file["/exchange/norm-0-g2"],
            g2_stderr=self.data_file["/exchange/norm-0-stderr"],
            tau=self.data_file["/exchange/tau"],
            g2_partials_twotime=self.data_file["/exchange/g2partials"],
            g2_twotime=self.data_file["/exchange/g2full"],
            # TODO figure out how to access large amount of data
            # "C": "C_shaped_array"
            mask=self.data_file["/xpcs/mask"],
            dqmap=["/xpcs/dqmap"],
            dqlist=self.data_file["/xpcs/dqlist"],
            dphilist=self.data_file["/xpcs/dphilist"],
            sqmap=self.data_file["/xpcs/sqmap"],
            sqlist=self.data_file["/xpcs/sqlist"],
            sphilist=self.data_file["/xpcs/sphilist"]
        )
        return xpcs

    def saxs1d_md(self):
        saxs1d = dict(
            I=self.data_file["..."],
            I_partial=self.data_file["..."]
        )
        return saxs1d

    def saxs2d_md(self):
        saxs2d = dict(
            I=self.data_file["..."]
        )
        return saxs2d

    def instrument_md(self):
        instrument = dict(
            count_time = self.data_file["..."],
            frame_time = self.data_file["..."],
            description = self.data_file["..."],
            distance = self.data_file["..."],
            x_pixel_size = self.data_file["..."],
            y_pixel_size = self.data_file["..."],
        )
        return instrument


