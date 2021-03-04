import pytest
from unisul_sync_gui.crawler import abc
from unisul_sync_gui.crawler.api import (
    AsyncRunner, 
    parse_request_url,
)

from urllib.parse import urlparse
from unittest.mock import MagicMock


def test_google_returns_200_ok(spider_factory):
    def assert_response_status(response, _):
        assert response.status == 200

    mock = MagicMock(side_effect=assert_response_status)

    request = abc.Request(url='https://www.google.com/', 
                          callback=mock)
    spider = spider_factory(request)

    runner = AsyncRunner(spider)
    runner.start()

    mock.assert_called_once()


def test_runs_one_worker_at_time_by_default(assert_crawl_urls):
    expected = ['http://fake1.com', 'http://fake2.com', 'http://fake3.com']
    assert_crawl_urls(expected)


def test_uses_absolute_and_relative_urls(assert_crawl_urls):
    inputs = ['http://absolute.com/', '/']
    expected = ['http://absolute.com/', 'https://www.fake.com/']

    assert_crawl_urls(expected, inputs) 


def test_fails_when_callback_fail(spider_factory, crawler_factory):
    mock = MagicMock(side_effect=NameError('some'))

    request = abc.Request(url='anything', 
                          callback=mock)

    spider = spider_factory(request)
    runner = crawler_factory(spider)

    with pytest.raises(NameError):
        runner.start()


def test_uses_spider_scheme(spider_factory, crawler_factory):
    expected = 'http'

    def test_scheme(_, request):
        assert urlparse(request.url).scheme == expected

    mock = MagicMock(side_effect=test_scheme)

    request = abc.Request(url='/', 
                          callback=mock)

    spider = spider_factory(request)
    spider.scheme = expected

    runner = crawler_factory(spider)
    runner.start()

    mock.assert_called()


def test_fails_parse_relative_url_when_no_domain(spider_factory):
    request = abc.Request(url='/', 
                          callback=lambda: None)

    spider = spider_factory(request)

    # unset domain
    spider.domain = None

    with pytest.raises(ValueError):
        parse_request_url('/', spider)


def test_parse_request_url_prepend_preffix(spider_factory):
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
        request = abc.Request(url=url,
                            callback=lambda: None)

        spider = spider_factory(request)

        spider.preffix = preffix

        result = parse_request_url(request.url, spider)

        assert result == expected or result.startswith(expected)