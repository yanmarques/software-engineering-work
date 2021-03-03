import pytest
from unisul_sync_gui.crawler import abc

from pathlib import Path


class FakeDumper(abc.IODumper):
    def write_fp(self, fp, data, **kwargs):
        pass

    def read_fp(self, fp, **kwargs):
        pass


class FakeExporter(abc.ListExporter):
    def dumper_factory(self, path):
        return FakeDumper(path)
    
    def should_export(self, item):
        return True


@pytest.fixture
def fake_exporter(tmp_path):
    file_path = tmp_path / Path('out')
    fake_exp = FakeExporter(file_path)
    return fake_exp


@pytest.fixture
def mock_exporter_write(fake_exporter):
    def wrapper(mock):
        fake_exporter.dumper.write_fp = mock
        return fake_exporter

    return wrapper


@pytest.fixture
def exp_write_args(mock_exporter_write):
    return mock_exporter_write(lambda _, *args, **__: args)


@pytest.fixture
def exp_write_kwargs(mock_exporter_write):
    return mock_exporter_write(lambda *_, **kwargs: kwargs)
