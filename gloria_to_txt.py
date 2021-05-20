import sys
import os

from gloria.gloria import GLORIAFile

if __name__ == '__main__':
    try:
        infile = sys.argv[1]
    except IndexError:
        progname = os.path.basename(sys.argv[0])
        print('Usage: {} infile.dat [outfile.txt]'.format(progname))
        sys.exit(2)

    # We can optionally be given an explicit output filename 
    outfile = sys.argv[2] if len(sys.argv) > 2 else None
 
    with GLORIAFile(infile) as f:
        f.to_text(outfile)

