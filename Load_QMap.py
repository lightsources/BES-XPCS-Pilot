
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

import datetime
import h5py
import logging
import os

DATAFILE = 'B009_Aerogel_1mm_025C_att1_Lq0_001_0001-10000.hdf'
NEXUSFILE = 'NeXus_file.hdf'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    ###### Initialization ######
    fn_dir = os.path.abspath(".")
    full_filename = os.path.join(fn_dir, DATAFILE)

    def get_key(key):
        v = result[key][()]
        if isinstance(v, bytes):
            # convert b'string' to 'string'
            v = v.decode()
        return v

    md = {}
    with h5py.File(full_filename, 'r') as result:
        dqmap = np.squeeze(result.get('/xpcs/dqmap')[()])
        md["file_name"] = DATAFILE
        md["start_time"] = get_key("/measurement/instrument/source_begin/datetime")
        md["end_time"] = get_key("/measurement/instrument/source_end/datetime")
        for key in """
                data_folder
                datafilename
                parent_folder
                root_folder
                specfile
                """.split():
            md[key] = get_key(f"/measurement/instrument/acquisition/{key}")
        for key in """
                manufacturer
                geometry
                """.split():
            md[key] = get_key(f"/measurement/instrument/detector/{key}")
        for key in """
                adu_per_photon
                distance
                exposure_time
                exposure_period
                gain
                sigma
                x_binning
                x_dimension
                x_pixel_size
                y_binning
                y_dimension
                y_pixel_size""".split():
            # these are from number arrays of length 1
            md[key] = result[f"/measurement/instrument/detector/{key}"][()][0]
        for key in """
                Version
                analysis_type
                input_file_local
                normalization_method
                """.split():
            md[f"xpcs-{key}"] = get_key(f"/xpcs/{key}")



    ###### plot the Q map to PDF file ######
    logger.info(f'plot Q map to file: Q_Map.pdf')
    fig, ax = plt.subplots(1, 1, figsize=(15, 10))
    im = ax.imshow(dqmap, cmap='jet', interpolation='none')
    fig.colorbar(im, ax=ax)
    plt.rc('font', size=20)
    plt.savefig('Q_Map.pdf', dpi=100, format='pdf', facecolor='w', edgecolor='w', transparent=False)

    logger.info(f'masks: {np.max(dqmap)} Map')
    logger.info(f'rows: {dqmap.shape[0]} Map')
    logger.info(f'columns: {dqmap.shape[1]} Map')

    ###### build the masks ######
    mask = np.zeros([np.max(dqmap),dqmap.shape[0],dqmap.shape[1]])

    for ii in np.arange(np.max(dqmap)):
        logger.debug(f'defining mask {ii}')
        mask[ii,:,:] = np.where(dqmap == ii, 1, 0)  

    ###### plot the masks to PDF file ######
    logger.info(f'plot mask to file: tmp.pdf')
    fig, ax = plt.subplots(1, 1, figsize=(15, 10))
    im = ax.imshow(mask[10,:,:], cmap='gray', interpolation='none')
    fig.colorbar(im, ax=ax)
    plt.rc('font', size=20)
    plt.savefig('tmp.pdf', dpi=100, format='pdf', facecolor='w', edgecolor='w', transparent=False)

    ###### write the NeXus data file ######
    nexus_file = os.path.join(fn_dir, NEXUSFILE)
    timestamp = datetime.datetime.now().isoformat(sep=" ", timespec="seconds")
    logger.info(f'write NeXus file: {NEXUSFILE}')
    with h5py.File(nexus_file, "w") as nx:
        # point to the default data to be plotted
        nx.attrs['default']          = 'entry'
        # give the HDF5 root some more attributes
        nx.attrs['file_name']        = nexus_file
        nx.attrs['file_time']        = timestamp
        nx.attrs['instrument']       = 'APS XPCS at 8-ID-I'
        nx.attrs['creator']          = __file__             # TODO: better choice?
        nx.attrs['HDF5_Version']     = h5py.version.hdf5_version
        nx.attrs['h5py_version']     = h5py.version.version

        # create the NXentry group
        nxentry = nx.create_group('entry')
        nxentry.attrs['NX_class'] = 'NXentry'
        nxentry.attrs['default'] = 'data'
        nxentry.create_dataset('title', data=DATAFILE)     # TODO: better choice?

        # create the NXentry group
        nxdata = nxentry.create_group('data')
        nxdata.attrs['NX_class'] = 'NXdata'
        nxdata.attrs['signal'] = 'image'      # Y axis of default plot

        # signal data
        ds = nxdata.create_dataset('image', data=[0,1,2,3,4,5,6,7], compression='gzip', compression_opts=9) # FIXME: use actual image data
        ds.attrs['units'] = 'scale'
        ds.attrs['long_name'] = 'FIXME: XPCS image data'    # suggested Y axis plot label
        ds.attrs['target'] = ds.name    # for the NeXus link

        nxmask = nxdata.create_group('mask')
        nxmask.attrs['NX_class'] = 'NXarraymask'
        nxmask.create_dataset('usage', data="Intersectable")   # TODO: check this
        nxmask.create_dataset('mask', data=mask, compression='gzip', compression_opts=5)
        nxmask["data_link"] = nx[ds.name]

        nxnote = nxmask.create_group('annotation')
        nxnote.attrs['NX_class'] = 'NXnote'
        for k, v in md.items():
            nxnote.create_dataset(k, data=v)


if __name__ == "__main__":
    main()


"""
Any of this should go into the NeXus file?

structure of the input HDF5 file:

(py37) mintadmin@mintadmin-VirtualBox ~/.../Desktop/2020-03-04 XPCS NeXus $ punx tree -a -m 0 B009_Aerogel_1mm_025C_att1_Lq0_001_0001-10000.hdf 

!!! WARNING: this program is not ready for distribution.

/mnt/host_c_drive/Users/Pete/Desktop/2020-03-04 XPCS NeXus/B009_Aerogel_1mm_025C_att1_Lq0_001_0001-10000.hdf
  exchange
    baselineErrFIT1:float64[1,27] = [ ... ]
    baselineErrFIT2:float64[1,27] = [ ... ]
    baselineFIT1:float64[1,27] = [ ... ]
    baselineFIT2:float64[1,27] = [ ... ]
    contrastErrFIT1:float64[1,27] = [ ... ]
    contrastErrFIT2:float64[1,27] = [ ... ]
    contrastFIT1:float64[1,27] = [ ... ]
    contrastFIT2:float64[1,27] = [ ... ]
    exponentErrFIT2:float64[1,27] = [ ... ]
    exponentFIT2:float64[1,27] = [ ... ]
    frameSum:float32[2,10000] = [ ... ]
    g2avgFIT1:float64[48,1,27] = [ ... ]
    g2avgFIT2:float64[48,1,27] = [ ... ]
    norm-0-g2:float32[48,27] = [ ... ]
    norm-0-stderr:float32[48,27] = [ ... ]
    partition-mean-partial:float32[10,270] = [ ... ]
    partition-mean-total:float32[1,270] = [ ... ]
    partition_norm_factor:float32[1,1] = [ ... ]
    pixelSum:float32[516,1556] = [ ... ]
    tau:float32[1,48] = [ ... ]
    tauErrFIT1:float64[1,27] = [ ... ]
    tauErrFIT2:float64[1,27] = [ ... ]
    tauFIT1:float64[1,27] = [ ... ]
    tauFIT2:float64[1,27] = [ ... ]
    timestamp_clock:float64[2,10000] = [ ... ]
    timestamp_tick:float64[2,10000] = [ ... ]
  measurement
    instrument
      acquisition
        angle:float64[1,1] = [ ... ]
        attenuation:float64[1,1] = [ ... ]
        beam_center_x:float64[1,1] = [ ... ]
        beam_center_y:float64[1,1] = [ ... ]
        beam_size_H:float64[1,1] = [ ... ]
        beam_size_V:float64[1,1] = [ ... ]
        ccdxspec:float64[1,1] = [ ... ]
        ccdzspec:float64[1,1] = [ ... ]
        compression:CHAR = ENABLED
        dark_begin:uint64[1,1] = [ ... ]
        dark_end:uint64[1,1] = [ ... ]
        data_begin:uint64[1,1] = [ ... ]
        data_end:uint64[1,1] = [ ... ]
        data_folder:CHAR = B009_Aerogel_1mm_025C_att1_Lq0_001/
        datafilename:CHAR = B009_Aerogel_1mm_025C_att1_Lq0_001_00001-10000.imm
        parent_folder:CHAR = russell202002
        root_folder:CHAR = /data/2020-1/russell202002/
        specfile:CHAR = russell20200218
        specscan_dark_number:uint64[1,1] = [ ... ]
        specscan_data_number:uint64[1,1] = [ ... ]
        stage_x:float64[1,1] = [ ... ]
        stage_z:float64[1,1] = [ ... ]
        stage_zero_x:float64[1,1] = [ ... ]
        stage_zero_z:float64[1,1] = [ ... ]
        xspec:float64[1,1] = [ ... ]
        zspec:float64[1,1] = [ ... ]
      detector
        adu_per_photon:float64[1,1] = [ ... ]
        bit_depth:uint32[1,1] = [ ... ]
        blemish_enabled:CHAR = ENABLED
        burst_enabled:CHAR = DISABLED
        distance:float64[1,1] = [ ... ]
        efficiency:float64[1,1] = [ ... ]
        exposure_period:float64[1,1] = [ ... ]
        exposure_time:float64[1,1] = [ ... ]
        flatfield:float64[516,1556] = [ ... ]
        flatfield_enabled:CHAR = ENABLED
        gain:uint32[1,1] = [ ... ]
        geometry:CHAR = TRANSMISSION
        kinetics_enabled:CHAR = DISABLED
        lld:float64[1,1] = [ ... ]
        manufacturer:CHAR = LAMBDA
        sigma:float64[1,1] = [ ... ]
        x_binning:uint32[1,1] = [ ... ]
        x_dimension:uint32[1,1] = [ ... ]
        x_pixel_size:float64[1,1] = [ ... ]
        y_binning:uint32[1,1] = [ ... ]
        y_dimension:uint32[1,1] = [ ... ]
        y_pixel_size:float64[1,1] = [ ... ]
        burst
          first_usable_burst:uint32[1,1] = [ ... ]
          last_usable_burst:uint32[1,1] = [ ... ]
          number_of_bursts:uint32[1,1] = [ ... ]
        kinetics
          first_usable_window:uint32[1,1] = [ ... ]
          last_usable_window:uint32[1,1] = [ ... ]
          top:uint32[1,1] = [ ... ]
          window_size:uint32[1,1] = [ ... ]
        roi
          x1:uint32[1,1] = [ ... ]
          x2:uint32[1,1] = [ ... ]
          y1:uint32[1,1] = [ ... ]
          y2:uint32[1,1] = [ ... ]
      source_begin
        beam_intensity_incident:float64[1,1] = [ ... ]
        beam_intensity_transmitted:float64[1,1] = [ ... ]
        current:float64[1,1] = [ ... ]
        datetime:CHAR = Tue Feb 18 15:30:30 2020
        energy:float64[1,1] = [ ... ]
      source_end
        current:float64[1,1] = [ ... ]
        datetime:CHAR = Tue Feb 18 15:30:45 2020
    sample
      orientation:float64[1,3] = [ ... ]
      temperature_A:float64[1,1] = [ ... ]
      temperature_A_set:float64[1,1] = [ ... ]
      temperature_B:float64[1,1] = [ ... ]
      temperature_B_set:float64[1,1] = [ ... ]
      thickness:float64[1,1] = [ ... ]
      translation:float64[1,3] = [ ... ]
      translation_table:float64[1,3] = [ ... ]
  xpcs
    Version:CHAR = b'1.0'
    analysis_type:CHAR = b'Multitau'
    avg_frames:uint64[1,1] = [ ... ]
    avg_frames_burst:uint64[1,1] = [ ... ]
    batches:uint64[1,1] = [ ... ]
    blemish_enabled:CHAR = ENABLED
    compression:CHAR = ENABLED
    dark_begin:uint64[1,1] = [ ... ]
    dark_begin_todo:uint64[1,1] = [ ... ]
    dark_end:uint64[1,1] = [ ... ]
    dark_end_todo:uint64[1,1] = [ ... ]
    data_begin:uint64[1,1] = [ ... ]
    data_begin_todo:uint64[1,1] = [ ... ]
    data_end:uint64[1,1] = [ ... ]
    data_end_todo:uint64[1,1] = [ ... ]
    delays_per_level:uint64[1,1] = [ ... ]
    delays_per_level_burst:uint64[1,1] = [ ... ]
    dnophi:float64[1,1] = [ ... ]
    dnoq:float64[1,1] = [ ... ]
    dphilist:float64[1,27] = [ ... ]
    dphispan:float64[1,2] = [ ... ]
    dqlist:float64[1,27] = [ ... ]
    dqmap:uint32[516,1556] = [ ... ]
    dqspan:float64[1,28] = [ ... ]
    dynamic_mean_window_size:uint64[1,1] = [ ... ]
    flatfield_enabled:CHAR = ENABLED
    input_file_local:CHAR = B009_Aerogel_1mm_025C_att1_Lq0_001_00001-10000.imm
    input_file_remote:CHAR = russell202002/B009_Aerogel_1mm_025C_att1_Lq0_001/B009_Aerogel_1mm_025C_att1_Lq0_001_00001-10000.imm
    kinetics:CHAR = DISABLED
    lld:float64[1,1] = [ ... ]
    mask:uint8[516,1556] = [ ... ]
    normalization_method:CHAR = b'TRANSMITTED'
    normalize_by_framesum:uint64[1,1] = [ ... ]
    normalize_by_smoothed_img:uint64[1,1] = [ ... ]
    num_g2partials:uint64[1,1] = [ ... ]
    output_data:CHAR = b'/exchange'
    output_file_local:CHAR = B009_Aerogel_1mm_025C_att1_Lq0_001_00001-10000.imm
    output_file_remote:CHAR = b'output/results'
    qmap_hdf5_filename:CHAR = b'/home/8-id-i/partitionMapLibrary/2020-1/russell202002_qmap_Silica_Lq0_S270_D27_log.h5'
    qphi_bin_to_process:uint64[1,1] = [ ... ]
    sigma:float64[1,1] = [ ... ]
    smoothing_method:CHAR = b'symmetric'
    snophi:float64[1,1] = [ ... ]
    snoq:float64[1,1] = [ ... ]
    specfile:CHAR = russell20200218
    specscan_dark_number:uint64[1,1] = [ ... ]
    specscan_data_number:uint64[1,1] = [ ... ]
    sphilist:float64[1,270] = [ ... ]
    sphispan:float64[1,2] = [ ... ]
    sqlist:float64[1,270] = [ ... ]
    sqmap:uint32[516,1556] = [ ... ]
    sqspan:float64[1,271] = [ ... ]
    static_mean_window_size:uint64[1,1] = [ ... ]
    stride_frames:uint64[1,1] = [ ... ]
    stride_frames_burst:uint64[1,1] = [ ... ]
    swbinX:uint64[1,1] = [ ... ]
    swbinY:uint64[1,1] = [ ... ]
    twotime2onetime_window_size:uint64[1,1] = [ ... ]

"""