import os
from unisul_sync_gui.crawler.api import MiddlewareAwareCrawler
from unisul_sync_gui.builtin_plugins.sync_gui.crawler import (
    spiders,
    items,
)
from aiohttp.test_utils import make_mocked_coro


def get_test_html(filename):
    cwd = os.path.dirname(os.path.abspath(os.path.realpath(__file__)))
    with open(os.path.join(cwd, filename), 'r') as io_r:
        return io_r.read()


def test_subject_parser(middleware_factory, mock_crawler_session):
    expected = [
        items.Subject(name='Foo', class_id='123'),
        items.Subject(name='Bar', class_id='321'),
        items.Subject(name='Baz', class_id='213'),
    ]

    async def patch_response(response):
        content = get_test_html('subject-spider-response.html')
        response.text = make_mocked_coro(content)

    async def with_items(subjects):
        names = [s.name for s in subjects]
        assert names == expected

    middleware = middleware_factory(spiders.SubjectSpider())
    middleware.on_response = patch_response
    middleware.on_processed_response = with_items

    crawler = MiddlewareAwareCrawler(middleware)
    mock_crawler_session(crawler)
    crawler.start()