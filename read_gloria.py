import argparse

from gloria import GLORIAFile

def main():
    parser = argparse.ArgumentParser(description='print the header, a sample of the data, and diagnostics, from the given GLORIA file')
    parser.add_argument('infile', help='GLORIA file')
    args = parser.parse_args()

    with GLORIAFile(args.infile) as f:
        data = f.read()

        print('Number of scans = {}'.format(len(data['scans'])))

        # The following: for scan in data['scans']: would iterate over all
        # scans in the file.  Here though, we just show a summary of the
        # first scan

        print('Summary of the first scan:')
        scan = data['scans'][0]
        pass_number = int(scan['pass_number'])
        scan_number = int(scan['scan_number'])
        samples = scan['sonar_samples'][0]

        print('Number of samples = {}'.format(len(samples)))
        print('Scan header:')

        for key in f.DEFAULTS['scan_record_header_keys']:
            print(f.format_header_line(key, scan[key][0]))

        print(f.format_header_line(f.DEFAULTS['datetime_var_name'], f.get_scan_datetime_str(scan)))

        # Show a small selection of the first scan's samples
        if len(samples) > 0:
            nsamples = 10 if len(samples) > 10 else len(samples)
            print('scan {}: first {} samples = {}'.format(scan_number, nsamples, samples[0:nsamples]))

if __name__ == '__main__':
    main()

