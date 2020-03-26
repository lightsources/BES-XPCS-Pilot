

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from scipy.optimize import curve_fit

import h5py

plt.rc('font', size=20)

###### Read the hdf file ######

fn_dir='./'
fn = f'B009_Aerogel_1mm_025C_att1_Lq0_001_0001-10000.hdf'

with h5py.File(fn_dir+fn, 'r') as HDF_Result:
    Iq = HDF_Result.get('/exchange/partition-mean-total')[()]
    ql_sta = np.squeeze(HDF_Result.get('/xpcs/sqlist')[()])
    ql_dyn = np.squeeze(HDF_Result.get('/xpcs/dqlist')[()])
    t0 = np.squeeze(HDF_Result.get('/measurement/instrument/detector/exposure_period')[()])
    t_el = t0*np.squeeze(HDF_Result.get('/exchange/tau')[()])
    g2 = HDF_Result.get('/exchange/norm-0-g2')[()]
    g2_err = HDF_Result.get('/exchange/norm-0-stderr')[()]
    Int_2D = HDF_Result.get('/exchange/pixelSum')[()]



#### Plot g2 for the first 9 ROI's ####

cv_x = 3
cv_y = 3

cv_dim = cv_x*cv_y

fig, axs = plt.subplots(cv_x, cv_y, figsize=(20, 15))
for ii in range(cv_x):
    for jj in range(cv_y):
        dim = ii*cv_y+jj  
        ax = axs[ii,jj]
        ax.set_xscale('log')
        ax.set_ylim(1, 1.1)
        ax.errorbar(t_el, g2[:,dim], yerr=g2_err[:,dim], 
            fmt='ro', markersize=9, markerfacecolor='none')
        ax.text(0.6, 0.2, ('Q = %5.4f $\AA^{-1}$' %ql_dyn[dim]), horizontalalignment='center',
                verticalalignment='center', transform=ax.transAxes)
plt.savefig('g2_ave.pdf', dpi=100, format='pdf', facecolor='w', edgecolor='w', transparent=True)


###### Plot the 2D SAXS Pattern ######

QZ_colormap = plt.cm.jet
QZ_colormap.set_under(color='w')


fig, ax = plt.subplots(1, 1, figsize=(15, 10))
im = ax.imshow(Int_2D, cmap=QZ_colormap, norm=LogNorm(vmin=5e-3, vmax=5e-1), interpolation='none')
fig.colorbar(im, ax=ax)
plt.rc('font', size=20)
plt.savefig('Int_2D.pdf', dpi=100, format='pdf', facecolor='w', edgecolor='w', transparent=False)



###### Plot the 1D SAXS Pattern (I vs. Q) ######

fig, ax = plt.subplots(1, 1, figsize=(12, 10))
plt.xticks([1e-3,1e-2,1e-1])
plt.yticks([1e-6,1e-5,1e-4,1e-3])
# plt.xlim(1.5e-3, 1e-1)
# plt.ylim(3e-5, 1e-3)
plt.rc('font', size=20)
ax.plot(ql_sta, np.squeeze(Iq), color='r', fillstyle='none', 
    marker='o', markersize=10)
ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlabel('Q ($\AA^{-1}$)')
ax.set_ylabel('Int. (Photon/Pixel/Frame)')
plt.savefig('IvsQ.pdf', dpi=100, format='pdf', facecolor='w', edgecolor='w', transparent=True)
