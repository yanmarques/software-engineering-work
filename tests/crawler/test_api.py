import pytest
from unisul_sync_gui.crawler import http
from unisul_sync_gui.crawler.api import (
    AsyncCrawler, 
    MiddlewareAwareCrawler,
)

from unittest.mock import MagicMock, Mock
from aiohttp.test_utils import make_mocked_coro


def test_google_returns_200_ok(spider_factory):
    async def assert_response_status(response, _):
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


def test_middleware_crawler_calls_success_events(fake_middleware, mock_crawler_session):
    fake_middleware.on_request = make_mocked_coro()
    fake_middleware.on_response = make_mocked_coro()
    fake_middleware.on_processed_response = make_mocked_coro()

    crawler = MiddlewareAwareCrawler(fake_middleware)
    mock_crawler_session(crawler)

    crawler.start()

    fake_middleware.on_request.assert_called()
    fake_middleware.on_response.assert_called()
    fake_middleware.on_processed_response.assert_called()


def test_middleware_crawler_calls_process_error_events(spider_factory, 
                                                       middleware_factory,
                                                       mock_crawler_session):
    def process(_, __):
        raise NameError('any')

    request = http.Request(url='/', callback=process)
    spider = spider_factory(request)

    middleware = middleware_factory(spider)
    middleware.on_response_process_error = make_mocked_coro()

    crawler = MiddlewareAwareCrawler(middleware)
    mock_crawler_session(crawler)

    with pytest.raises(NameError):
        crawler.start()

    middleware.on_response_process_error.assert_called()


def test_middleware_crawler_calls_request_error_events(fake_middleware, mock_crawler_session):
    fake_middleware.on_request_error = make_mocked_coro(None)

    crawler = MiddlewareAwareCrawler(fake_middleware)

    def request_ctx(*_, **__):
        raise NameError('any')

    mock_crawler_session(crawler, mock=request_ctx)

    with pytest.raises(NameError):
        crawler.start()

    fake_middleware.on_request_error.assert_called()


def test_middleware_crawler_keep_going_on_error_when_return_true(fake_middleware, 
                                                                 mock_crawler_session):
    # mock function that return True
    fake_middleware.on_request_error = make_mocked_coro(True)

    crawler = MiddlewareAwareCrawler(fake_middleware)

    def request_ctx(*_, **__):
        raise NameError('any')

    mock_crawler_session(crawler, mock=request_ctx)

    crawler.start()

    fake_middleware.on_request_error.assert_called()
