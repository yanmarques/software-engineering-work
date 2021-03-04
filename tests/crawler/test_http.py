import pytest
from unisul_sync_gui.crawler import http

from urllib.parse import urlparse


def test_request_uses_spider_scheme(spider_factory):
    expected = 'http'

    request = http.Request(url='/', 
                           callback=None)

    spider = spider_factory(request)
    spider.scheme = expected

    result = request.parse_url(spider)

    assert urlparse(result).scheme == expected


def test_request_uses_spider_domain_with_relative_urls(spider_factory):
    domain = 'test.com'
    expected = f'https://{domain}/'

    request = http.Request(url='/', 
                           callback=None)

    spider = spider_factory(request)
    spider.domain = domain

    result = request.parse_url(spider)

    assert result == expected


def test_fails_parse_relative_url_when_missing_spider_domain(spider_factory):
    request = http.Request(url='/', 
                          callback=None)

    spider = spider_factory(request)

    # unset domain
    spider.domain = None

    with pytest.raises(ValueError):
        request.parse_url(spider)


def test_parsing_request_url_prepends_preffix(spider_factory):
    expected = 'https://www.fake.com/foo/bar'

    options = [
        ('bar/', 'foo'),
        ('bar/', 'foo/'),
        ('bar/', '/foo'),
        ('bar/', '/foo/'),

        ('/bar', 'foo'),
        ('/bar', 'foo/'),
        ('/bar', '/foo'),
        ('/bar', '/foo/'),

        ('/bar/', 'foo/'),
        ('/bar/', 'foo'),
        ('/bar/', '/foo'),
        ('/bar/', '/foo/'),
    ]

    for url, preffix in options:
        request = http.Request(url=url,
                            callback=lambda: None)

        spider = spider_factory(request)

        spider.preffix = preffix

        result = request.parse_url(spider)

        assert result == expected or result.startswith(expected)