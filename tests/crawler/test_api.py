import pytest
from unisul_sync_gui.crawler import abc, http
from unisul_sync_gui.crawler.api import (
    AsyncCrawler, 
)

from urllib.parse import urlparse
from unittest.mock import MagicMock


def test_google_returns_200_ok(spider_factory):
    def assert_response_status(response, _):
        assert response.status == 200

    mock = MagicMock(side_effect=assert_response_status)

    request = http.Request(url='https://www.google.com/', 
                          callback=mock)
    spider = spider_factory(request)

    runner = AsyncCrawler(spider)
    runner.start()

    mock.assert_called_once()


def test_runs_one_worker_at_time_by_default(assert_crawl_urls):
    expected = ['http://fake1.com', 'http://fake2.com', 'http://fake3.com']
    assert_crawl_urls(expected)


def test_fails_when_callback_fail(spider_factory, crawler_factory):
    mock = MagicMock(side_effect=NameError('some'))

    request = http.Request(url='anything', 
                          callback=mock)

    spider = spider_factory(request)
    runner = crawler_factory(spider)

    with pytest.raises(NameError):
        runner.start()
