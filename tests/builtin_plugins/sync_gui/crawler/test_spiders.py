from unisul_sync_gui.builtin_plugins.sync_gui.crawler import (
    spiders,
    items,
)


def test_subject_parser(middleware_factory, crawler_auth_factory):
    async def with_response(response):
        assert response.status == 200

    middleware = middleware_factory(spiders.SubjectSpider())
    middleware.on_response = with_response

    crawler = crawler_auth_factory(middleware)
    crawler.start()


def test_subject_parser_loader(middleware_factory, crawler_auth_factory):
    async def with_subjects(subjects):
        assert len(subjects) != 0

    middleware = middleware_factory(spiders.SubjectSpider())
    middleware.on_processed_response = with_subjects

    crawler = crawler_auth_factory(middleware)
    crawler.start()
