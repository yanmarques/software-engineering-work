import pytest
from unisul_sync_gui import auth
from unisul_sync_gui.app import context
from unisul_sync_gui.crawler import (
    MiddlewareAwareCrawler,
)

class CrawlerSessionPatched(MiddlewareAwareCrawler):
    async def _handle_request(self, session, request):
        session.cookie_jar.update_cookies(context.http_session.cookies)
        return await super()._handle_request(session, request)


@pytest.fixture
def crawler_auth_factory():
    auth_service = auth.Authenticator()
    if not auth_service.logged:
        auth_service.try_from_disk()
        if not auth_service.logged:
            raise auth.AuthenticationException()
    
    return CrawlerSessionPatched
