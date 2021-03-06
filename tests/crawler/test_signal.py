import pytest
from unisul_sync_gui.crawler import MiddlewareAwareCrawler
from unisul_sync_gui.crawler import signal
from aiohttp.test_utils import make_mocked_coro


def test_subscribe_to_async_event(fake_spider, mock_crawler_session):
    async_mock = make_mocked_coro()

    crawler_signals = signal.CrawlerSignals()
    crawler_signals.on_request.connect(async_mock)

    middleware = signal.SignalingMiddleware(fake_spider, crawler_signals)
    crawler = MiddlewareAwareCrawler(middleware)
    mock_crawler_session(crawler)
    crawler.start()

    async_mock.assert_called()


@pytest.mark.asyncio
async def test_signal_freezes_listeners_after_first_event():
    crawler_signals = signal.CrawlerSignals()
    crawler_signals.on_request.connect(make_mocked_coro())

    await crawler_signals.on_request.emit()

    with pytest.raises(RuntimeError):
        crawler_signals.on_request.connect(make_mocked_coro())
