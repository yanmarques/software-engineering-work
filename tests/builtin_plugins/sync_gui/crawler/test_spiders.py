from unisul_sync_gui.crawler import http
from unisul_sync_gui.builtin_plugins.sync_gui.crawler import (
    spiders,
    items,
)


def test_book_spider_creates_two_request_loaders_per_subject(fake_loader):
    subjects = [
        items.Subject(name='foo', class_id='123'),
    ]

    def patch_request(loader, **kwargs):
        assert loader.subject == subjects[0]

        kwargs['callback'] = fake_loader.load
        return http.Request(**kwargs)

    spider = spiders.BookSpider(subjects)
    spider.request = patch_request

    requests = list(spider.start_requests())

    assert len(requests) == 2
