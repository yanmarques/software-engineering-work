import aiohttp
from . import abc

import os
import asyncio
from urllib.parse import urlparse


def parse_request_url(url: str, spider: abc.Spider):
    '''
    Transform the url according to spider settings.
    '''

    parse = urlparse(url)

    # relative urls
    if parse.netloc == '':
        if spider.domain is None:
            raise ValueError('Spider has no default domain')

        # set spider domain and scheme
        kwargs = dict(netloc=spider.domain,
                      scheme=spider.scheme)

        # needs a path preffix
        if spider.preffix is not None:
            preffixed_path = os.path.join(spider.preffix,
                                          parse.path.lstrip('/'))
            kwargs.update(path=preffixed_path)

        # fix url
        parse = parse._replace(**kwargs)

    return parse.geturl()


class AsyncRunner:
    def __init__(self,
                 spider: abc.Spider,
                 session_factory=None,
                 limit=None) -> None:
        '''
        Run parallel http requests from spider.

        spider: Holds information about what requests to make.
        session_factory: Factory function that returns a `aiohttp.ClientSession`.
        '''

        self.spider = spider
        self.session_factory = session_factory or aiohttp.ClientSession
        self.limit = limit or 1
        self.loop = asyncio.get_event_loop()

    def start(self):
        self.loop.run_until_complete(self._run())

    def _prepare_req(self, request: abc.Request):
        url = parse_request_url(request.url, self.spider)

        # set new url
        request.update(url=url)

        kwargs = request.to_dict()

        # remove callback key
        del kwargs['callback']

        return kwargs

    async def _http_req(self,
                        semaphore: asyncio.Semaphore, 
                        session: aiohttp.ClientSession,
                        request: abc.Request):
        async with semaphore:
            kwargs = self._prepare_req(request)

            async with session.request(**kwargs) as response:
                request.callback(response, request)

    async def _run(self):
        # orchestrate the limit of parallel workers
        sem = asyncio.Semaphore(self.limit)

        async with self.session_factory() as session:
            futures = [self._http_req(sem, session, request)
                       for request in self.spider.start_requests()]

            await asyncio.gather(*futures)