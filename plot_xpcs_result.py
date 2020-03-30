#!/usr/bin/env python

"""
Load and plot XPCS results
"""

import os

import h5py
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import numpy as np

import loaders


def plot_g2(xpcs):
    """
    Plot g2 for the first 9 ROIs
    """

    columns = 3
    rows = 3

    _fig, axs = plt.subplots(columns, rows, figsize=(20, 15))
    for ii in range(columns):
        for jj in range(rows):
            dim = ii*rows + jj
            ax = axs[ii, jj]
            ax.set_xscale('log')
            ax.set_ylim(1, 1.1)
            ax.errorbar(
                xpcs["t_el"],
                xpcs["g2"][:, dim],
                yerr=xpcs["g2_err"][:, dim],
                fmt='ro', markersize=9, markerfacecolor='none')
            ax.text(
                0.6, 0.2,
                (
                    f'Q = {xpcs["ql_dyn"][dim]:5.4f} '
                    r'$\AA^{-1}$'
                ),
                horizontalalignment='center',
                verticalalignment='center',
                transform=ax.transAxes)
    plt.savefig(
        'g2_ave.pdf', dpi=100, format='pdf', facecolor='w',
        edgecolor='w', transparent=True)


def plot_2d_saxs(xpcs):
    """
    Plot the 2D SAXS Pattern
    """
    custom_colormap = plt.cm.get_cmap("jet")
    custom_colormap.set_under(color='w')

    fig, ax = plt.subplots(1, 1, figsize=(15, 10))
    im = ax.imshow(
        xpcs["Int_2D"],
        cmap=custom_colormap,
        norm=LogNorm(vmin=5e-3, vmax=5e-1),
        interpolation='none')
    fig.colorbar(im, ax=ax)
    plt.rc('font', size=20)
    plt.savefig(
        'Int_2D.pdf', dpi=100, format='pdf', facecolor='w',
        edgecolor='w', transparent=False)


def plot_1d_saxs(xpcs):
    """
    Plot the 1D SAXS Pattern (I vs. Q)
    """
    _fig, ax = plt.subplots(1, 1, figsize=(12, 10))
    plt.xticks([1e-3, 1e-2, 1e-1])
    plt.yticks([1e-6, 1e-5, 1e-4, 1e-3])
    # plt.xlim(1.5e-3, 1e-1)
    # plt.ylim(3e-5, 1e-3)
    plt.rc('font', size=20)
    ax.plot(
        xpcs["ql_sta"],
        np.squeeze(xpcs["Iq"]),
        color='r', fillstyle='none',
        marker='o', markersize=10)
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel(r'Q ($\AA^{-1}$)')
    ax.set_ylabel('Int. (Photon/Pixel/Frame)')
    plt.savefig(
        'IvsQ.pdf', dpi=100, format='pdf',
        facecolor='w', edgecolor='w', transparent=True)


def main():
    """
    Here is what the program will do
    """
    full_filename = os.path.join(
        os.path.dirname(__file__),
        f'B009_Aerogel_1mm_025C_att1_Lq0_001_0001-10000.hdf'
    )
    xpcs = loaders.read_xpcs_results(full_filename)

    plt.rc('font', size=20)
    plot_g2(xpcs)
    plot_1d_saxs(xpcs)
    plot_2d_saxs(xpcs)


if __name__ == "__main__":
    main()
