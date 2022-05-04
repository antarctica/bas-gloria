import argparse

from gloria import GLORIAFile

def main():
    parser = argparse.ArgumentParser(description='read a GLORIA file and write to another GLORIA file, optionally subsetting the data ')
    parser.add_argument('infile', help='GLORIA file')
    parser.add_argument('outfile', help='GLORIA file')
    parser.add_argument('-s', '--scans', help='only write out the first SCANS scans', dest='scans', default=None, type=int)
    parser.add_argument('-a', '--samples', help='only write out the first SAMPLES samples', dest='samples', default=None, type=int)
    args = parser.parse_args()

    # We can optionally select a subset of scans and/or samples for output.
    # These have to be range objects
    if args.scans:
        args.scans = range(args.scans)
    if args.samples:
        args.samples = range(args.samples)
 
    with GLORIAFile(args.infile) as f:
        f.to_gloria(args.outfile, scans=args.scans, samples=args.samples)

if __name__ == '__main__':
    main()

