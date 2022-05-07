import os

import numpy as np

import pytest

from gloria import __version__, GLORIAFile

base = os.path.dirname(__file__)

def test_version():
    assert __version__ == '0.2.0'

@pytest.fixture
def short_test_data():
    in_file = base + '/data/short-test-data.dat'

    with GLORIAFile(in_file) as f:
        data = f.read()
 
    return data

@pytest.fixture
def mock_open(mocker):
    mocker.patch('builtins.open', mocker.mock_open())
 
def test_override_path_in_open():
    non_existent_file = base + '/data/non-existent-file'
    existent_file = base + '/data/short-test-data.dat'

    f = GLORIAFile(non_existent_file)

    with pytest.raises(FileNotFoundError):
        f.open()
        f.read()
        f.close()

    # Override the path given to the constructor with a valid path
    f.open(existent_file)
    f.read()
    f.close()

def test_optional_path_in_open():
    in_file = base + '/data/short-test-data.dat'

    f = GLORIAFile(in_file)
    f.open()
    f.read()
    f.close()

def test_optional_path_in_constructor():
    in_file = base + '/data/short-test-data.dat'

    f = GLORIAFile()
    f.open(in_file)
    f.read()
    f.close()

def test_read_ok():
    in_file = base + '/data/short-test-data.dat'

    with GLORIAFile(in_file) as f:
        data = f.read()
        assert len(data['scans']) == 20
        scan = data['scans'][0]
        assert int(scan['pass_number']) == 245
        assert int(scan['scan_number']) == 1
        samples = scan['sonar_samples'][0]
        assert len(samples) == 994

def test_scan_datetime_str_ok(short_test_data):
    f = GLORIAFile()
    scan = short_test_data['scans'][0]
    assert f.get_scan_datetime_str(scan) == '1989-03-29T12:00:00'

def test_scan_datetime_str_custom_output_format_ok(short_test_data, mocker):
    f = GLORIAFile()

    mocker.patch.dict(f.DEFAULTS, {'datetime_output_format': '%d/%m/%Y %H:%M:%S'})
    scan = short_test_data['scans'][0]
    assert f.get_scan_datetime_str(scan) == '29/03/1989 12:00:00'

def test_format_header_line_ok():
    f = GLORIAFile()
    s = f.format_header_line('pass_number', 245)
    assert s == 'pass_number=245'

def test_format_header_line_custom_delim_ok(mocker):
    f = GLORIAFile()

    mocker.patch.dict(f.DEFAULTS, {'header_line_delim': ':'})
    s = f.format_header_line('pass_number', 245)
    assert s == 'pass_number:245'

def test_write_text_scan_header_ok(short_test_data, mock_open):
    non_existent_file = base + '/data/non-existent-file'
    f = GLORIAFile()
    scan = short_test_data['scans'][0]

    with open(non_existent_file, 'w') as fout:
        f.write_text_scan_header(fout, scan)
        fout.write.assert_any_call('pass_number=245\n')

def test_write_text_scan_data_ok(short_test_data, mock_open):
    non_existent_file = base + '/data/non-existent-file'
    f = GLORIAFile()
    scan = short_test_data['scans'][0]
    expected = f"scan={','.join(str(n) for n in scan['sonar_samples'][0])}\n"

    with open(non_existent_file, 'w') as fout:
        f.write_text_scan_data(fout, scan)
        fout.write.assert_any_call(expected)

def test_write_data_ok(short_test_data, mock_open):
    non_existent_file = base + '/data/non-existent-file'
    f = GLORIAFile()
    f.data = short_test_data

    with open(non_existent_file, 'wb') as fout:
        f.write_data(fout)
        fout.write.assert_called()
        # The last line written should be the last scan
        assert np.array_equal(fout.write.call_args[0][0], f.data['scans'][-1])

def test_write_data_rewrite_dimensions(short_test_data, mock_open):
    non_existent_file = base + '/data/non-existent-file'
    f = GLORIAFile()
    f.data = short_test_data

    with open(non_existent_file, 'wb') as fout:
        f.write_data(fout, scans=range(10))
        fout.write.assert_called()
        # The last line written should be the 10th scan
        assert np.array_equal(fout.write.call_args[0][0], f.data['scans'][9])

    # As the GLORIA recored is fixed-width, when subsetting samples, they're
    # not actually removed from the record, rather they are set to zero
    scan = short_test_data['scans'][-1]
    expected = scan.copy()
    expected['sonar_samples'][0] = np.zeros(994, dtype='B')
    expected['sonar_samples'][0][:10] = scan['sonar_samples'][0][:10]

    with open(non_existent_file, 'wb') as fout:
        f.write_data(fout, samples=range(10))
        fout.write.assert_called()
        assert np.array_equal(fout.write.call_args[0][0], expected)

def test_write_data_rewrite_dimensions_invalid_kwarg_type(short_test_data, mock_open):
    non_existent_file = base + '/data/non-existent-file'
    f = GLORIAFile()
    f.data = short_test_data

    with open(non_existent_file, 'wb') as fout:
        # Keyword argument `scans` (and `samples`) must be a range object
        with pytest.raises(AttributeError):
            f.write_data(fout, scans=10)

    with open(non_existent_file, 'wb') as fout:
        with pytest.raises(AttributeError):
            f.write_data(fout, samples=10)

