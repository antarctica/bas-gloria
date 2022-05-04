import argparse

from gloria import GLORIAFile

def main():
    parser = argparse.ArgumentParser(description='convert a GLORIA file to a netCDF4 file')
    parser.add_argument('infile', help='GLORIA file')
    parser.add_argument('outfile', help='converted netCDF file', default=None, nargs='?')
    args = parser.parse_args()
 
    with GLORIAFile(args.infile) as f:
        f.to_netcdf(args.outfile)

if __name__ == '__main__':
    main()

