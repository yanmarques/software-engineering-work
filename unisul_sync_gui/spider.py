from . import cookies, __version__
from .book_bot import settings as default_crawler_settings
from .config import path_name_of
from .app import context
from scrapy.crawler import CrawlerRunner
from crochet import setup, wait_for

# config global reactor interface
setup()


def crawl(spider, settings={}, timeout=10.0, *args, **kwargs):
    for k, v in get_default_settings().items():
        settings.setdefault(k, v)

    @wait_for(timeout=timeout)
    def wrapper():
        runner = CrawlerRunner(settings=settings)
        return runner.crawl(spider, *args, **kwargs)
    
    return wrapper()


def get_default_settings():
    defaults = get_project_settings()
    defaults.setdefault('USER_AGENT', f'UnisulSync {__version__}')
    defaults.setdefault('COOKIES_PERSISTENCE_DIR', cookies.cookie_name())

    for k, v in context.config.get('crawler_settings', {}).items():
        defaults[k] = v

    return defaults


def get_project_settings():
    return parse_scrapy_settings(default_crawler_settings)


def parse_scrapy_settings(settings):
    defaults = {}
    for key in dir(settings):
        if not key.startswith('__'):
            defaults[key] = getattr(settings, key)
    return defaults