from . import cookies
from .book_bot import settings as default_crawler_settings
from .app import context
from .config import path_name_of
from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from multiprocessing import Process, Queue

import scrapy
import os


def crawl(spider, settings={}, *args, **kwargs):
    assert spider is not None, 'Spider must not be null'
    
    for k, v in _default_settings().items():
        settings.setdefault(k, v)

    def run(queue):
        try:
            os.chdir(context.book_bot_path)
            runner = CrawlerRunner(settings=settings)
            deferred = runner.crawl(spider, *args, **kwargs)
            deferred.addBoth(lambda _: reactor.stop())
            reactor.run()
            queue.put(None)
        except Exception as e:
            queue.put(e)
        
    queue = Queue()
    main_proc = Process(target=run, args=(queue,))
    main_proc.start()
    result = queue.get()
    main_proc.join()
    return result


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