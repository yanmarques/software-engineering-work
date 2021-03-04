import aiohttp
from . import abc

import asyncio
from urllib.parse import urlparse


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
        # handle relative urls
        url = urlparse(request.url)
        if url.netloc == '':
            if self.spider.domain is None:
                raise ValueError('Spider has no default domain')

            url = url._replace(netloc=self.spider.domain,
                         scheme=self.spider.scheme)

        request.update(url=url.geturl())

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