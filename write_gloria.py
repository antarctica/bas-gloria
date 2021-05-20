import sys
import os

from gloria.gloria import GLORIAFile

if __name__ == '__main__':
    try:
        infile = sys.argv[1]
        outfile = sys.argv[2]
    except IndexError:
        progname = os.path.basename(sys.argv[0])
        print('Usage: {} infile.dat outfile.dat [scans [samples]]'.format(progname))
        sys.exit(2)

    (scans, samples) = (None, None)

    # We can optionally select a subset of scans and/or samples for output
    if len(sys.argv) > 3:
        scans = range(int(sys.argv[3]))
    if len(sys.argv) > 4:
        samples = range(int(sys.argv[4]))
 
    with GLORIAFile(infile) as f:
        f.to_gloria(outfile, scans=scans, samples=samples)

