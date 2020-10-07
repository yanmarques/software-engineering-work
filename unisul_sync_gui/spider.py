from . import cookies
from .book_bot import settings as default_crawler_settings
from .config import path_name_of
from .app import context
from scrapy.crawler import CrawlerRunner
from crochet import setup, wait_for
setup()


def crawl(spider, settings={}, timeout=10.0, *args, **kwargs):
    for k, v in _default_settings().items():
        settings.setdefault(k, v)

    @wait_for(timeout=timeout)
    def wrapper():
        runner = CrawlerRunner(settings=settings)
        return runner.crawl(spider, *args, **kwargs)
    
    return wrapper()


def _default_settings():
    defaults = _get_from_project()
    defaults.setdefault('USER_AGENT', 'UnisulSync v0.0.0')
    defaults.setdefault('COOKIES_PERSISTENCE_DIR', cookies.cookie_name())

    for k, v in context.config.get('crawler_settings', {}).items():
        defaults[k] = v

    return defaults


def _get_from_project():
    defaults = {}
    for key in dir(default_crawler_settings):
        if not key.startswith('__'):
            defaults[key] = getattr(default_crawler_settings, key)
    return defaults