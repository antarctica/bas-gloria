import sys
import os
import argparse

from matplotlib import pyplot as plt
import numpy as np
from netCDF4 import Dataset

from gloria.gloria import GLORIAFile

def construct_sonargram(plt, mat, xaxis, yaxis, xlim=None, ylim=None,
                        xlabel='scan number',
                        ylabel='sample number',
                        contrast=1.0, cmap='gray', aspect='auto'):
    """
    Construct the given matrix as a sonargram, held in the given
    matplotlib.pyplot object.  Call plt.show() to plot the sonargram

    :param plt: The matplotlib.pyplot object that contains the plot
    :type plt: matplotlib.pyplot object
    :param mat: The data
    :type mat: numpy.matrix
    :param xaxis: The x-axis coordinates
    :type xaxis: numpy.linspace
    :param yaxis: The y-axis coordinates
    :type yaxis: numpy.linspace
    :param xlim: The x-axis limits
    :type xlim: list
    :param ylim: The y-axis limits
    :type ylim: list
    :param xlabel: The x-axis label
    :type xlabel: str
    :param ylabel: The y-axis label
    :type ylabel: str
    :param contrast: Scale factor for the plot contrast
    :type contrast: float
    :param cmap: Colour map for the plot
    :type cmap: str
    :param aspect: Controls the aspect ratio of the plot
    :type aspect: str or float
    """

    dx = xaxis[1] - xaxis[0]
    dy = yaxis[1] - yaxis[0]
    xlim = xlim or [min(xaxis), max(xaxis)]
    ylim = ylim or [max(yaxis), min(yaxis)]
    extent = [min(xaxis) - dx/2.0, max(xaxis) + dx/2.0, max(yaxis) + dy/2.0, min(yaxis) - dy/2.0]
    std_contrast = np.nanmax(np.abs(mat)[:])

    plt.imshow(mat, cmap=cmap, extent=extent, aspect=aspect, vmin=-std_contrast/contrast, vmax=std_contrast/contrast)

    plt.gca().set_xlabel(xlabel)
    plt.gca().set_ylabel(ylabel)
    plt.xlim(xlim)
    plt.ylim(ylim)

def parse_cmdln():
    """
    Parse the command line options and arguments

    :returns: The parsed command line arguments object
    :rtype: argparse.Namespace object
    """

    epilog = """Examples

Plot the given GLORIA .dat file as a sonargram:

python3 plot_gloria.py filename.dat

Plot the given converted netCDF file as a sonargram:

python3 plot_gloria.py filename.nc

Plot the given GLORIA file as a sonargram, increasing the contrast:

python3 plot_gloria.py -c 10 filename.dat

Same as above, but with a blue-white-red colour map:

python3 plot_gloria.py -c 10 -m bwr filename.dat

Plot the first scan from the given GLORIA file:

python3 plot_gloria.py -s filename.dat

Plot the first 6 scans, in a 3x2 grid:

python3 plot_gloria.py -s -g 3 2 filename.dat
"""

    parser = argparse.ArgumentParser(description='plot GLORIA data, either from a .dat file, or a converted netCDF file', epilog=epilog, formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('filename', help='filename')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('-r', '--sonargram', help='plot a sonargram', action='store_const', dest='type', const='sonargram')
    group.add_argument('-s', '--scans', help='plot individual scans', action='store_const', dest='type', const='scans')
    parser.set_defaults(type='sonargram')

    parser.add_argument('-g', '--grid', help='plot the first nrows x ncols scans', dest='grid', nargs=2, default=[1, 1], type=int)
    parser.add_argument('-c', '--contrast', help='contrast for the sonargram', dest='contrast', default=1.0, type=float)
    parser.add_argument('-m', '--cmap', help='colour map for the sonargram', dest='cmap', default='gray')

    args = parser.parse_args()

    return args

if __name__ == '__main__':
    args = parse_cmdln()
    suffix = os.path.splitext(args.filename)[1]

    if suffix.lower() == '.dat':
        with GLORIAFile(args.filename) as f:
            data = f.read()
    elif suffix.lower() == '.nc':
        with Dataset(args.filename, 'r') as f:
            data = {'scans': []}

            for key in f.groups:
                scan = {}

                # Reconstruct a simile of the scan header
                for hkey in vars(f.groups[key]):
                    scan[hkey] = [getattr(f.groups[key], hkey)]

                # We make a copy, otherwise data is invalid after file is closed
                scan['sonar_samples'] = [f.groups[key].variables['scan'][:]]
                data['scans'].append(scan)
    else:
        raise ValueError('Unknown or unsupported file type: {}'.format(suffix))

    if args.type == 'scans':
        (nrows, ncols) = args.grid
        fig = plt.figure()

        # Plot the given number of scans in an nrows x ncols grid
        for i in range(nrows * ncols):
            try:
                scan = data['scans'][i]
                ax = fig.add_subplot(nrows, ncols, i + 1)

                # Only plot axis labels on the left side, and bottom
                if i % ncols == 0: ax.set_ylabel('amplitude')
                if i + 1 > (nrows - 1) * ncols: ax.set_xlabel('samples')

                # Plot the scan label in the legend to save space
                ax.plot(scan['sonar_samples'][0], label='scan {:.0f}'.format(scan['scan_number'][0]))
                ax.legend()
            except IndexError:
                pass
    else:
        nscans = len(data['scans'])
        nsamples = len(data['scans'][0]['sonar_samples'][0])
        xaxis = np.linspace(1.0, float(nscans), nscans)
        yaxis = np.linspace(1.0, float(nsamples), nsamples)

        # Store each scan as a column in a matrix
        cols = np.zeros((nsamples, nscans))

        for i, scan in enumerate(data['scans']):
            cols[:,i] = scan['sonar_samples'][0]

        mat = np.asmatrix(cols)
        ylim = [max(yaxis), 0]

        # Plot the vertical scans as a sonargram
        construct_sonargram(plt, mat, xaxis, yaxis, ylim=ylim, contrast=args.contrast, cmap=args.cmap)

    plt.suptitle(os.path.basename(args.filename))
    plt.show()
