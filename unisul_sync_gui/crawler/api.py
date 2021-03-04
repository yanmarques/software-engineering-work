import aiohttp
from . import abc, http

import asyncio


class AsyncCrawler:
    def __init__(self,
                 spider: abc.Spider,
                 session_factory=None,
                 limit=None) -> None:
        '''
        Run parallel http requests from spider.

        spider: Holds information about what requests to make.
        session_factory: Factory function that returns a `aiohttp.ClientSession`.
        limit: Maximum number of parallel tasks. Default: 1.
        '''

        self.spider = spider
        self.session_factory = session_factory or aiohttp.ClientSession
        self.limit = limit or 1
        self.loop = asyncio.get_event_loop()

    def start(self):
        self.loop.run_until_complete(self._run())

    def _prepare_req(self, request: http.Request):
        url = request.parse_url(self.spider)

        # set new url
        request.update(url=url)

        kwargs = request.to_dict()

        # remove callback key
        del kwargs['callback']

        return kwargs

    async def _http_req(self,
                        semaphore: asyncio.Semaphore, 
                        session: aiohttp.ClientSession,
                        request: http.Request):
        async with semaphore:
            kwargs = self._prepare_req(request)

            async with session.request(**kwargs) as response:
                self._with_response(request, response)

    def _with_response(self, request, response):
        request.callback(response, request)

    async def _run(self):
        # orchestrate the limit of parallel workers
        sem = asyncio.Semaphore(self.limit)

        async with self.session_factory() as session:
            futures = [self._http_req(sem, session, request)
                       for request in self.spider.start_requests()]

            await asyncio.gather(*futures)