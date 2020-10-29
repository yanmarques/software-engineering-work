import os

import scrapy
from .eva_parser import BookSpider
from unisul_sync_gui.book_bot.loaders import BookLoader
from unisul_sync_gui.book_bot.utils import os_files, http


class BookDownloaderSpider(scrapy.Spider):
    name = 'books_downloader'
    allowed_domains = http.EVA_DOMAIN

    custom_settings = {
        'DOWNLOAD_TIMEOUT': 1200,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 100,
        'CONCURRENT_REQUESTS': 100,
        
        'ITEM_PIPELINES': {
            'unisul_sync_gui.book_bot.pipelines.SyncPipeline': 100,
        },
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert hasattr(self, 'book_uri'), 'Missing argument: book_uri' 

    @classmethod
    def from_crawler(cls, crawler):
        spider = cls(
            book_uri=crawler.settings.get('BOOK_EXPORTER_URI'),
            custom_books=crawler.settings.get('CUSTOM_BOOKS')
        )
        spider.crawler = crawler
        return spider

    def start_requests(self):
        yield http.web_open(callback=self.synchronize)

    def synchronize(self, response):
        for item in self.load_books():
            book_item = self.dict_to_book(item)

            if book_item['is_external'] and not book_item['seems_downloadable']:
                continue

            download_url = book_item['download_url'] 

            # normalize url when not full-url
            if not book_item['is_external'] and not response.url in download_url:
                book_item['download_url'] = response.urljoin(download_url)
            yield book_item

    def dict_to_book(self, data: dict):
        return BookLoader.from_dict(data)

    def load_books(self):
        if hasattr(self, 'custom_books'):
            return self.custom_books
        return os_files.load_sync_data(self.book_uri)