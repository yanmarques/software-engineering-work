import pytest
from unisul_sync_gui.crawler import http
from unisul_sync_gui.crawler.api import (
    AsyncCrawler, 
    MiddlewareAwareCrawler,
)

from unittest.mock import MagicMock, Mock


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


def test_middleware_crawler_calls_success_events(fake_spider, mock_crawler_session):
    mock = Mock()
    mock.spider = fake_spider

    crawler = MiddlewareAwareCrawler(mock)
    mock_crawler_session(crawler)

    crawler.start()

    mock.on_request.assert_called()
    mock.on_response.assert_called()
    mock.on_processed_response.assert_called()


def test_middleware_crawler_calls_process_error_events(spider_factory, mock_crawler_session):
    def process(_, __):
        raise NameError('any')

    request = http.Request(url='/', callback=process)
    spider = spider_factory(request)

    middleware = Mock()
    middleware.spider = spider

    crawler = MiddlewareAwareCrawler(middleware)
    mock_crawler_session(crawler)

    with pytest.raises(NameError):
        crawler.start()

    middleware.on_response_process_error.assert_called()


def test_middleware_crawler_calls_request_error_events(fake_spider, mock_crawler_session):
    middleware = Mock()
    middleware.spider = fake_spider

    crawler = MiddlewareAwareCrawler(middleware)

    def request_ctx(*_, **__):
        raise NameError('any')

    mock_crawler_session(crawler, mock=request_ctx)

    with pytest.raises(NameError):
        crawler.start()

    middleware.on_request_error.assert_called()


def test_middleware_crawler_keep_going_on_error_when_return_true(fake_spider, 
                                                                 mock_crawler_session):
    middleware = Mock()
    middleware.spider = fake_spider

    # mock function that return True
    middleware.on_request_error = lambda *_, **__: True

    crawler = MiddlewareAwareCrawler(middleware)

    def request_ctx(*_, **__):
        raise NameError('any')

    mock_crawler_session(crawler, mock=request_ctx)

    crawler.start()

    middleware.on_request_error.assert_called()
