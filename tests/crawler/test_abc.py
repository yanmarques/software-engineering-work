import pytest

import os
from unittest.mock import Mock

    
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


@pytest.mark.asyncio
async def test_item_loader_with_all_items(fake_loader):
    expected = [
        {'test': 'foo',},
        {'test': 'bar',},
        {'test': 'baz',},
    ]

    result = await fake_loader.load()

    assert result == expected


@pytest.mark.asyncio
async def test_item_loader_not_includes_invalid_item(fake_loader):
    blacklist = ['foo']
    expected = [
        {'test': 'bar',},
        {'test': 'baz',},
    ]

    # apply blacklist
    fake_loader.is_valid = lambda item: item['test'] not in blacklist

    result = await fake_loader.load()

    assert result == expected


@pytest.mark.asyncio
async def test_item_loader_process_item_completely_changes_items(fake_loader):
    expected = [1, 2, 3]
    
    fake_loader.process_item = Mock(side_effect=expected)

    result = await fake_loader.load()

    assert result == expected


@pytest.mark.asyncio
async def test_item_loader_fails_with_empty_xpath(fake_loader):
    fake_loader.xpath_tree = Mock(return_value='.//*[@id="not-exists"]')

    with pytest.raises(ValueError):
        await fake_loader.load()