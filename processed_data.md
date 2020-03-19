# Processed data

describe how we will write processed data

* goes into a NXprocess group
* blend the (new) Load_XPCS_Result.py into the Load_QMap.py file and write the full NeXus file as an example.
  * *blend* includes only data handling and not plotting part

This codes reads the data (we want) from the Data Exchange HDF5 file:

```
with h5py.File(os.path.join(fn_dir, fn), 'r') as HDF_Result:
    Iq = HDF_Result.get('/exchange/partition-mean-total')[()]
    ql_sta = np.squeeze(HDF_Result.get('/xpcs/sqlist')[()])
    ql_dyn = np.squeeze(HDF_Result.get('/xpcs/dqlist')[()])
    t0 = np.squeeze(HDF_Result.get('/measurement/instrument/detector/exposure_period')[()])
    t_el = t0*np.squeeze(HDF_Result.get('/exchange/tau')[()])
    g2 = HDF_Result.get('/exchange/norm-0-g2')[()]
    g2_err = HDF_Result.get('/exchange/norm-0-stderr')[()]
    Int_2D = HDF_Result.get('/exchange/pixelSum')[()]
```
