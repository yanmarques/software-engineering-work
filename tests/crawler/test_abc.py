import os

    
def test_exports_all(exp_write_args):
    expected = [1, 2, 3]

    result = exp_write_args.export(expected)

    assert result == (expected,)


def test_io_export_with_kwargs(exp_write_kwargs):
    kw_expected = {'foo': 'bar'}

    result = exp_write_kwargs.export([], **kw_expected)

    assert result == kw_expected


def test_io_export_creates_file(fake_exporter):
    fake_exporter.export([])
    assert os.path.isfile(fake_exporter.dumper.path)


def test_io_export_use_utf8_by_default(mock_exporter_write):
    def assert_fp_is_utf8(fp, _):
        assert fp.encoding == 'utf-8'

    mock_exp = mock_exporter_write(assert_fp_is_utf8)

    mock_exp.export([])