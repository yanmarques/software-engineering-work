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
            await self._handle_request(session, request)

    async def _with_response(self, request, response):
        return await request.callback(response, request)

    async def _handle_request(self, 
                        session: aiohttp.ClientSession, 
                        request: http.Request):
        # transform request object into a dict
        kwargs = self._prepare_req(request)

        async with session.request(**kwargs) as response:
            await self._with_response(request, response)

    async def _run(self):
        # orchestrate the limit of parallel workers
        sem = asyncio.Semaphore(self.limit)

        async with self.session_factory() as session:
            futures = [self._http_req(sem, session, request)
                       for request in self.spider.start_requests()]

            await asyncio.gather(*futures)


class MiddlewareAwareCrawler(AsyncCrawler):
    def __init__(self,
                 middleware: abc.Middleware, 
                 *args, 
                 **kwargs) -> None:
        '''
        Regular crawler that intercept strategic method calls and
        dispatch them to the middleware.

        middleware: Listens to a number of events.
        '''
        super().__init__(middleware.spider, *args, **kwargs)
        self.middleware = middleware

    async def _with_response(self, request, response):
        await self.middleware.on_response(response)
        
        try:
            result = await super()._with_response(request, response)
            await self.middleware.on_processed_response(result)
        except Exception as exc:
            await self._on_error(self.middleware.on_response_process_error,
                           exc, 
                           response)

    async def _handle_request(self, session, request):
        await self.middleware.on_request(request)

        try:
            await super()._handle_request(session, request)
        except Exception as exc:
            await self._on_error(self.middleware.on_request_error,
                           exc, 
                           request)

    async def _on_error(self, cb, error, *args):
        if await cb(error, *args) is not True:
            raise error