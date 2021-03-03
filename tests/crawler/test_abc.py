from unisul_sync_gui.crawler import abc

import os
from pathlib import Path


class FakeDumper(abc.IODumper):
    def write_fp(self, fp, data, **kwargs):
        pass


class FakeExporter(abc.ListExporter):
    def __init__(self, path):
        dumper = FakeDumper(path)
        super().__init__(dumper)
    
    def should_export(self):
        return True


def test_io_export_with_kwargs(tmp_path):
    kw_expected = {'foo': 'bar'}

    def assert_kwargs(_, __, **kwargs):
        assert kwargs == kw_expected

    file_path = tmp_path / Path('out')
    fake_exp = FakeExporter(file_path)
    
    # patch write function
    fake_exp.dumper.write_fp = assert_kwargs

    fake_exp.export([], **kw_expected)


def test_io_export_creates_file(tmp_path):
    file_path = tmp_path / Path('out')
    fake_exp = FakeExporter(file_path)

    fake_exp.export([])

    assert os.path.isfile(file_path)

def test_io_export_use_utf8_by_default(tmp_path):
    def assert_fp_is_utf8(fp, _, **__):
        assert fp.encoding == 'utf-8'

    file_path = tmp_path / Path('any')
    fake_exp = FakeExporter(file_path)
    
    # patch write function
    fake_exp.dumper.write_fp = assert_fp_is_utf8

    fake_exp.export([])