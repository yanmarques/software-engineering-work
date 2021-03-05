from unisul_sync_gui.builtin_plugins.sync_gui.crawler import spiders
from unisul_sync_gui.app import context
from unisul_sync_gui.crawler import (
    MiddlewareAwareCrawler,
)

from aiohttp.test_utils import make_mocked_coro


class CrawlerSessionPatched(MiddlewareAwareCrawler):
    async def _handle_request(self, session, request):
        session.cookie_jar.update_cookies(context.http_session.cookies)
        return await super()._handle_request(session, request)


def test_subject_parser(middleware_factory):
    async def with_response(response):
        assert response.status == 200

    middleware = middleware_factory(spiders.SubjectSpider())
    middleware.on_response = with_response

    crawler = MiddlewareAwareCrawler(middleware)
    crawler.start()
