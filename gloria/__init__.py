###############################################################################
# Project: GLORIA
# Purpose: Class to encapsulate a GLORIA file
# Author:  Paul M. Breen
# Date:    2020-05-19
###############################################################################

__version__ = '0.2.0'

import os
import sys
import datetime

import numpy as np
from netCDF4 import Dataset

class GLORIAFile(object):
    """
    Context manager for reading and writing GLORIA files
    """

    TYPE_SCAN_RECORD = np.dtype([
    ('pass_number', '>u2'),
    ('scan_number', '>u2'),
    ('hour_mark_flag', 'B'),
    ('slant_range_correction_code', 'B'),
    ('zero_flag', 'B'),
    ('pulse_repetition_period', 'B'),
    ('vehicle_heading', 'a3'),
    ('year', 'a2'),
    ('edge_mark_start', '>u2'),
    ('sonar_samples', 'B', 994),
    ('edge_mark_end', '>u2'),
    ('julian_day', 'a3'),
    ('hours', 'a2'),
    ('minutes', 'a2'),
    ('seconds', 'a2'),
    ('checksum', '>u2'),
    ('unused', '>u2')
    ])

    SCAN_RECORD_HEADER_KEYS = ['pass_number','scan_number','hour_mark_flag','slant_range_correction_code','zero_flag','pulse_repetition_period','vehicle_heading','year','edge_mark_start','edge_mark_end','julian_day','hours','minutes','seconds','checksum','unused']
    SCAN_RECORD_INTEGER_KEYS = ['pass_number','scan_number','hour_mark_flag','slant_range_correction_code','zero_flag','pulse_repetition_period','edge_mark_start','edge_mark_end','checksum','unused']
    SCAN_RECORD_DATETIME_KEYS = ['year','julian_day','hours','minutes','seconds']
    SCAN_RECORD_STRING_KEYS = SCAN_RECORD_DATETIME_KEYS + ['vehicle_heading']

    DATA_VAR_NAME = 'scan'
    DATETIME_VAR_NAME = 'datetime'

    DEFAULTS = {
        'type_scan_record': TYPE_SCAN_RECORD,
        'scan_record_header_keys': SCAN_RECORD_HEADER_KEYS,
        'scan_record_integer_keys': SCAN_RECORD_INTEGER_KEYS,
        'scan_record_datetime_keys': SCAN_RECORD_DATETIME_KEYS,
        'scan_record_string_keys': SCAN_RECORD_STRING_KEYS,
        'header_line_delim': '=',
        'header_line_eol': '\n',
        'datetime_input_format': '%y %j %H %M %S',
        'datetime_output_format': '%Y-%m-%dT%H:%M:%S',
        'data_type': 'B',
        'data_var_name': DATA_VAR_NAME,
        'datetime_var_name': DATETIME_VAR_NAME,
        'data_file_suffix': '.dat',
        'text_suffix': '.txt',
        'netcdf_suffix': '.nc',
        'netcdf_add_history': True,
        'netcdf_group_name': 'scan{:.0f}',
        'netcdf_dim_name': 'samples',
        'netcdf_var_name': DATA_VAR_NAME,
        'netcdf_attrs': {
            'units': '1',
            'long_name': 'Scan Samples'
        }
    }

    def __init__(self, path=None):
        """
        Constructor

        :param path: Path to the file
        :type path: str
        """

        self.path = path
        self.fp = None
        self.data = None

    def __enter__(self):
        """
        Enter the runtime context for this object

        The file is opened

        :returns: This object
        :rtype: GLORIAFile
        """

        return self.open(self.path)

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """
        Exit the runtime context for this object

        The file is closed

        :returns: False
        :rtype: bool
        """

        self.close()

        return False         # This ensures any exception is re-raised

    def open(self, path=None, mode='r'):
        """
        Open the given file

        :param path: Path to the file
        :type path: str
        :param mode: Mode in which to open the file
        :type mode: str
        :returns: This object
        :rtype: GLORIAFile
        """

        if path:
            self.path = path

        self.fp = open(self.path, mode)

        return self

    def close(self):
        """
        Close the file

        :returns: This object
        :rtype: GLORIAFile
        """

        self.fp.close()
        self.fp = None

        return self

    def read_data(self):
        """
        Read the data file

        * The scans are available in the scans list

        :returns: The parsed scans
        :rtype: dict
        """

        self.data = {'scans': []}

        while True:
            scan = np.fromfile(self.fp, dtype=self.DEFAULTS['type_scan_record'], count=1)

            if len(scan) > 0:
                self.data['scans'].append(scan)
            else:
                break

        return self.data

    def read(self):
        """
        Read the data file

        :returns: The parsed scans
        :rtype: dict
        """

        self.read_data()

        return self.data
 
    def format_datetime(self, dt):
        """
        Format the given datetime object as a string

        :param dt: The datetime
        :type dt: datetime.datetime
        :returns: The datetime as a string
        :rtype: str
        """

        return dt.strftime(self.DEFAULTS['datetime_output_format'])
 
    def get_scan_datetime(self, scan):
        """
        Get the datetime of the given scan from its date/time components

        :param scan: The scan record
        :type scan: type_scan_record
        :returns: The datetime of the scan
        :rtype: datetime.datetime
        """

        in_fmt = self.DEFAULTS['datetime_input_format']
        dt_components = [scan[key][0].decode('utf-8') or '0' for key in self.DEFAULTS['scan_record_datetime_keys']]
        dt_str = '{} {} {} {} {}'.format(*dt_components)
        dt = datetime.datetime.strptime(dt_str, in_fmt)

        return dt
 
    def get_scan_datetime_str(self, scan):
        """
        Get the datetime of the given scan as a formatted string

        :param scan: The scan record
        :type scan: type_scan_record
        :returns: The datetime of the scan as a string
        :rtype: str
        """

        return self.format_datetime(self.get_scan_datetime(scan))

    def format_header_line(self, key, value):
        """
        Format a raw header line from the given key and value

        :param key: The header item key
        :type key: str
        :param value: The header item value
        :type value: str
        :returns: The formatted raw header line
        :rtype: str
        """

        if key in self.DEFAULTS['scan_record_integer_keys']:
            fmt = '{}{}{:.0f}'
        else:
            fmt = '{}{}{}'

        # Strings are read as raw byte arrays, so convert to utf-8 strings
        if key in self.DEFAULTS['scan_record_string_keys']:
            value = value.decode('utf-8') or '0'

        return fmt.format(key, self.DEFAULTS['header_line_delim'], value)
 
    def write_text_scan_header(self, fp, scan):
        """
        Write the scan header as text to the given file object

        :param fp: The open file object of the output file
        :type fp: file object
        :param scan: The scan record
        :type scan: type_scan_record
        """

        eol = self.DEFAULTS['header_line_eol']

        for key in self.DEFAULTS['scan_record_header_keys']:
            line = self.format_header_line(key, scan[key][0])
            fp.write(line + eol)

        # Add date/time components as single datetime string, for convenience
        line = self.format_header_line(self.DEFAULTS['datetime_var_name'], self.get_scan_datetime_str(scan))
        fp.write(line + eol)

    def write_text_scan_data(self, fp, scan):
        """
        Write the scan data as text to the given file object

        :param fp: The open file object of the output file
        :type fp: file object
        :param scan: The scan record
        :type scan: type_scan_record
        """

        fp.write(self.DEFAULTS['data_var_name'] + self.DEFAULTS['header_line_delim'] + ','.join(str(n) for n in scan['sonar_samples'][0]) + self.DEFAULTS['header_line_eol'])

    def write_text(self, fp):
        """
        Write the scans as text to the given file object

        :param fp: The open file object of the output file
        :type fp: file object
        """

        for scan in self.data['scans']:
            self.write_text_scan_header(fp, scan)
            self.write_text_scan_data(fp, scan)

    def write_data(self, fp, scans=None, samples=None):
        """
        Write the scans to the given file object

        When rewriting the GLORIA data to a new file, the scans,
        and the samples for those selected scans, can be subsetted.  The
        scans and samples keyword arguments must specify a range object

        Note that as this is a fixed-width record format, the unwanted
        samples are padded with zeros

        :param fp: The open file object of the output file
        :type fp: file object
        :param scans: A range specifying the scans to be written
        :type scans: range object
        :param samples: A range specifying the samples to be written
        :type samples: range object
        """

        if not scans:
            scans = range(len(self.data['scans']))

        for scan in self.data['scans'][scans.start:scans.stop:scans.step]:
            # Sonar samples have to be fixed width, so we pad with zeros
            p = range(len(scan['sonar_samples'][0])) if not samples else samples
            subsamples = scan['sonar_samples'][0][p.start:p.stop:p.step]
            ldiff = len(scan['sonar_samples'][0]) - len(subsamples)
            scan['sonar_samples'][0] = np.pad(subsamples, (0,ldiff), mode='constant', constant_values=(0,0))
            fp.write(scan)

    def write(self, fp, scans=None, samples=None):
        """
        Write the data file and header file

        When rewriting the GLORIA data and header to new files, the scans,
        and the samples for those selected scans, can be subsetted.  The
        scans and samples keyword arguments must specify a range object

        Note that as this is a fixed-width record format, the unwanted
        samples are padded with zeros

        :param fp: The open file object of the output data file
        :type fp: file object
        :param scans: A range specifying the scans to be written
        :type scans: range object
        :param samples: A range specifying the samples to be written
        :type samples: range object
        """

        self.write_data(fp, scans=None, samples=None)

    def to_gloria(self, path, mode='wb', scans=None, samples=None):
        """
        Write the scans to the given file path as a GLORIA file

        When rewriting the GLORIA data to a new file, the scans,
        and the samples for those selected scans, can be subsetted.  The
        scans and samples keyword arguments must specify a range object

        Note that as this is a fixed-width record format, the unwanted
        samples are padded with zeros

        :param path: The path of the output file
        :type path: str
        :param mode: Mode in which to open the file
        :type mode: str
        :param scans: A range specifying the scans to be written
        :type scans: range object
        :param samples: A range specifying the samples to be written
        :type samples: range object
        """

        if self.data is None:
            self.read()

        with open(path, mode) as fout:
            self.write_data(fout, scans=scans, samples=samples)

    def to_text(self, path=None, mode='w'):
        """
        Write the scans to the given file path as a text file

        The default text file path is the same as the input file, but with
        a .txt suffix

        :param path: The path of the output file
        :type path: str
        :param mode: Mode in which to open the file
        :type mode: str
        """

        if self.data is None:
            self.read()

        path = path or os.path.splitext(self.path)[0] + self.DEFAULTS['text_suffix']

        with open(path, mode) as fout:
            self.write_text(fout)

    def to_netcdf(self, path=None, mode='w'):
        """
        Write the scans to the given file path as a netCDF4 file

        The default netCDF file path is the same as the input file, but with
        a .nc suffix

        :param path: The path of the output file
        :type path: str
        :param mode: Mode in which to open the file
        :type mode: str
        """

        if self.data is None:
            self.read()

        path = path or os.path.splitext(self.path)[0] + self.DEFAULTS['netcdf_suffix']

        ncfile = Dataset(path, mode)

        # Add the command line invocation to global history attribute
        if self.DEFAULTS['netcdf_add_history']:
            ncfile.history = ' '.join(sys.argv)

        # Write each scan as a netCDF4/HDF5 group
        for scan in self.data['scans']:
            group = ncfile.createGroup(self.DEFAULTS['netcdf_group_name'].format(scan['scan_number'][0]))

            # Write the scan header items as group attributes
            for key in self.DEFAULTS['scan_record_header_keys']:
                if key in self.DEFAULTS['scan_record_integer_keys']:
                    group.setncattr(key, int(scan[key][0]))
                else:
                    group.setncattr(key, scan[key][0])

            group.setncattr(self.DEFAULTS['datetime_var_name'], self.get_scan_datetime_str(scan))

            nsamples = len(scan['sonar_samples'][0])
            dtype = np.dtype(self.DEFAULTS['data_type'])

            dim = group.createDimension(self.DEFAULTS['netcdf_dim_name'], nsamples)

            data = group.createVariable(self.DEFAULTS['netcdf_var_name'], dtype, (self.DEFAULTS['netcdf_dim_name'],))
            data.setncatts(self.DEFAULTS['netcdf_attrs'])
            data[:] = scan['sonar_samples'][0]

        ncfile.close()

