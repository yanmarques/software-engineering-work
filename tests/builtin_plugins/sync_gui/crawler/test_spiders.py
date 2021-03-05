from unisul_sync_gui.builtin_plugins.sync_gui.crawler import spiders
from unisul_sync_gui.crawler import MiddlewareAwareCrawler

from aiohttp.test_utils import make_mocked_coro


def test_subject_parser(middleware_factory):
    async def with_response(response):
        assert response.status == 200

    middleware = middleware_factory(spiders.SubjectSpider())
    middleware.on_response = with_response

    crawler = MiddlewareAwareCrawler(middleware)
    crawler.start()
