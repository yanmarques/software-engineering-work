from unisul_sync_gui import spider


class objectview(object):
    def __init__(self, data):
        self.__dict__ = data


def test_parse_scrapy_reserved_settings(monkeypatch):
    fake_dict = {}

    valid_keys = ['bar', 'baz']
    not_valid_keys = ['__foo', '__'] 

    for key in valid_keys + not_valid_keys:
        fake_dict[key] = None

    # transform dict as object view
    settings = objectview(fake_dict)

    result = spider.parse_scrapy_settings(settings)

    assert list(result) == valid_keys