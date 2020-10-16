# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import os
import logging
from abc import ABC, abstractmethod

from unisul_sync_gui.app import context
from unisul_sync_gui.book_bot.utils import os_files
from twisted.internet import defer
from scrapy import Request
from scrapy.pipelines.files import FilesPipeline
from scrapy.exporters import JsonItemExporter
from scrapy.utils.log import failure_to_exc_info


logger = logging.getLogger(__name__)


class SyncPipeline(FilesPipeline):

    def media_to_download(self, request, info):
        def _onsuccess(result):
            if not result:
                return  # returning None force download

            logger.debug(
                'File (exists): Downloaded %(medianame)s from %(request)s',
                {'medianame': self.MEDIA_NAME, 'request': request},
                extra={'spider': info.spider}
            )
            self.inc_stats(info.spider, 'exists')

            return {'url': request.url, 'path': path, 'checksum': None}

        path = self.file_path(request, info=info)        
        dfd = defer.maybeDeferred(os_files.file_exists, self.store.basedir, path)
        dfd.addCallbacks(_onsuccess, lambda _: None)
        dfd.addErrback(
            lambda f:
            logger.error('Something went wrong.',
                         exc_info=failure_to_exc_info(f),
                         extra={'spider': info.spider})
        )
        return dfd

    def get_media_requests(self, item, info):
        if item['download_url']:
            yield Request(item['download_url'], meta={'book': item})

    def item_completed(self, results, item, info):
        context.signals.item_completed.emit(results=results,
                                            item=item, 
                                            info=info)
        return item

    def file_path(self, request, response=None, info=None):
        return request.meta['book'].path


class BaseExporter:
    def __init__(self, directory, export_file):
        self.file = os_files.open_sync_file(directory, export_file, 'wb')
        self.exporter = JsonItemExporter(self.file, 
                                        encoding='utf-8', 
                                        ensure_ascii=False,
                                        indent=2)
        self.exporter.start_exporting()

    @staticmethod
    def dir_from_crawler(crawler):
        return crawler.settings.get('EXPORTER_DIR')

    @abstractmethod
    def should_export(self, item):
        pass

    def process_item(self, item, spider):
        if self.should_export(item):
            self.exporter.export_item(item)
        return item

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()


class SubjectExportPipeline(BaseExporter):
    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            BaseExporter.dir_from_crawler(crawler),
            crawler.settings.get('SUBJECT_EXPORTER_URI')
        )

    def should_export(self, item):
        return item['name'] and item['class_id']

    
class BookExportPipeline(BaseExporter):
    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            BaseExporter.dir_from_crawler(crawler),
            crawler.settings.get('BOOK_EXPORTER_URI')
        )

    def process_item(self, item, spider):
        # fix when subject is a list, weird
        if isinstance(item['subject'], list):
            item['subject'] = item['subject'][0]
        super().process_item(item, spider)

    def should_export(self, item):
        return item['name'] and item['download_url'] and item['filename']


class MaxSubjectExportPipeline(SubjectExportPipeline):
    def should_export(self, item):
        return item['name'] and item['url']