from ... import spider, config
from ...app import context, cached_property
from ...book_bot.spiders import eva_parser

import os
import abc
import json


def find_available_pred(key):
    return default_predicates.get(key) or list(default_predicates.values())[0]


class FetchPredicate(abc.ABC):
    @abc.abstractmethod
    def name(self):
        pass

    @abc.abstractmethod
    def description(self):
        pass

    @abc.abstractmethod
    def should_fetch(self):
        pass


class BaseMediaLoader(abc.ABC):
    def __init__(self, predicate: FetchPredicate):
        super().__init__()
        self.predicate = predicate

    def load(self, force=False):
        spider_cls, filename = self.load_config()

        if force or self.predicate.should_fetch():
            self._fetch_from_spider(spider_cls, filename)

        path = config.path_name_of(filename)

        if os.path.exists(path):
            return self._from_file(path)

        return self.default()
    
    @abc.abstractmethod
    def load_config(self):
        pass

    def default(self):
        return []

    def _fetch_from_spider(self, spider_cls, exported_file):
        settings = {
            'EXPORTER_DIR': config.config_path()
        }

        spider.crawl(spider_cls, settings=settings, timeout=60.0)

    def _from_file(self, path):
        with open(path, encoding='utf8') as io_reader:
            return json.load(io_reader)

    @cached_property
    def _crawler_default_settings(self):
        return spider.get_project_settings()


class SubjectMediaLoader(BaseMediaLoader):
    def load_config(self):
        exported_file = self._crawler_default_settings['SUBJECT_EXPORTER_URI']
        return eva_parser.SubjectSpider, exported_file


class BookMediaLoader(BaseMediaLoader):
    def load_config(self):
        exported_file = self._crawler_default_settings['BOOK_EXPORTER_URI']
        return eva_parser.BookSpider, exported_file


class MostFrequentPredicate(FetchPredicate):
    def name(self):
        return 'sempre'

    def description(self):
        return '''
Sempre que aberto, serão baixadas as últimas atualizações do site da unisul.
'''

    def should_fetch(self):
        return True


class LeastFrequentPredicate(FetchPredicate):
    def name(self):
        return 'nunca'

    def description(self):
        return '''
Nunca uma atualização será baixada do site da unisul, sendo que apenas será mostrado
as informações já encontradas no computador.
'''

    def should_fetch(self):
        return False


# class DailyPredicate(LoadPredicate):
#     def should_load(self):
#         return True


default_predicates = {
    'always': MostFrequentPredicate(),
    'never': LeastFrequentPredicate()
}