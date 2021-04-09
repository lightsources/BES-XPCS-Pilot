import numpy as np
import datetime


md = {
    "/entry/SAXS_2D/data/I": np.random.uniform(0, 1, (16, 16)),
    "/entry/XPCS/data/g2": np.random.uniform(0, 1, (16, 16)),
    "/entry/XPCS/data/g2_stderr": np.random.uniform(0, 1, (16, 16)),
    "/entry/XPCS/data/tau": np.random.uniform(0, 1, (16, )),
    "/entry/XPCS/data/frameSum": np.random.uniform(0, 1, (16, 16)),
    "/entry/SAXS_1D/data/I": np.random.uniform(0, 1, (16, 16)),
    "/entry/SAXS_1D/data/I_partial": np.random.uniform(0, 1, (16, 16)),
    "/entry/XPCS/data/twotime/g2_partials_twotime": np.random.uniform(0, 1, (16, 16)),
    "/entry/XPCS/data/twotime/g2_twotime": np.random.uniform(0, 1, (16, 16)),
    "/entry/instrument/detector/count_time": 1e-4,
    "/entry/instrument/detector/frame_time":  1e-4,
    "/entry/instrument/detector/description": "hello new data format",
    "/entry/instrument/detector/distance": 4000,
    "/entry/instrument/detector/x_pixel_size": 75,
    "/entry/instrument/detector/y_pixel_size": 75,
    "/entry/instrument/monochromator/energy": 10.00,
    "/entry/datetime": str(datetime.datetime.now()),
    "/entry/sample/temperature_set": 300.0,
    "/entry/sample/temperature": 300.0,
    "/entry/sample/position_value": 1.0,
    "/entry/XPCS/instrument/mask/mask": np.random.uniform(0, 1, (16, 16)),
    "/entry/XPCS/instrument/mask/dqmap": np.random.uniform(0, 1, (16, 16)),
    "/entry/XPCS/instrument/mask/dqlist": np.random.uniform(0, 1, (16, )),
    "/entry/XPCS/instrument/mask/dphilist": np.random.uniform(0, 1, (16, )),
    "/entry/XPCS/instrument/mask/sqmap": np.random.uniform(0, 1, (16, 16)),
    "/entry/XPCS/instrument/mask/sqlist": np.random.uniform(0, 1, (16, )),
    "/entry/XPCS/instrument/mask/sphilist": np.random.uniform(0, 1, (16, ))
}

