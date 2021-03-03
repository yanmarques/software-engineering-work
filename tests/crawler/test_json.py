import os
from unisul_sync_gui.crawler import json


def test_dumps_then_load(json_dumper):
    expected = [1, 'foo']

    json_dumper.dump(expected)
    result = json_dumper.load()

    assert result == expected


def test_truncates_data(json_dumper):
    old_data = ['foo', 2]
    json_dumper.dump(old_data)

    expected_data = {'baz': 1}
    json_dumper.dump(expected_data)

    result = json_dumper.load()

    assert result == expected_data
