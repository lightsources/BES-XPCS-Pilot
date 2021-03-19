import h5py
import numpy as np


class APSLoader():

    def __init__(self, input_file):
        self.data_file = h5py.File(input_file, 'r')

    def get_c2t(self):
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

    #TODO move these to a more general approach for different loaders
    def xpcs_md(self):

        xpcs = dict(
            g2=self.data_file.get("/exchange/norm-0-g2"),
            g2_stderr=self.data_file.get("/exchange/norm-0-stderr"),
            tau=self.data_file.get("/exchange/tau"),
            g2_partials_twotime=self.data_file.get("/exchange/g2partials"),
            g2_twotime=self.data_file.get("/exchange/g2full"),
            # TODO figure out how to access large amount of data
            twotime=self.get_c2t(),
            mask=self.data_file.get("/xpcs/mask"),
            dqmap=self.data_file.get("/xpcs/dqmap"),
            dqlist=self.data_file.get("/xpcs/dqlist"),
            dphilist=self.data_file.get("/xpcs/dphilist"),
            sqmap=self.data_file.get("/xpcs/sqmap"),
            sqlist=self.data_file.get("/xpcs/sqlist"),
            sphilist=self.data_file.get("/xpcs/sphilist")
        )
        return xpcs

    def saxs1d_md(self):
        saxs1d = dict(
            I=self.data_file.get("..."),
            I_partial=self.data_file.get("...")
        )
        return saxs1d

    def saxs2d_md(self):
        saxs2d = dict(
            I=self.data_file.get("...")
        )
        return saxs2d

    def instrument_md(self):
        instrument = dict(
            count_time = self.data_file.get("..."),
            frame_time = self.data_file.get("..."),
            description = self.data_file.get("..."),
            distance = self.data_file.get("..."),
            x_pixel_size = self.data_file.get("..."),
            y_pixel_size = self.data_file.get("..."),
        )
        return instrument


