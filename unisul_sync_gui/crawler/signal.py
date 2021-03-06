from . import abc
from .. import signals


class CrawlerSignals:
    def __init__(self) -> None:
        '''
        Provides an interface for listening to crawler events. 
        '''

        self.on_request = signals.AsyncPysignal()

        self.on_response = signals.AsyncPysignal()
        self.on_processed_response = signals.AsyncPysignal()

        self.on_request_error = signals.AsyncPysignal()
        self.on_response_process_error = signals.AsyncPysignal()


class SignalingMiddleware(abc.Middleware):
    def __init__(self, 
                 spider: abc.Spider,
                 signals: CrawlerSignals) -> None:
        '''
        The middleware allows to easy subscribe to crawler events.

        It uses an instance of ``CrawlerSignals`` class as interface
        to publishing the events. 
        '''

        super().__init__(spider)
        self._signals = signals

    async def on_request(self, request):
        await self._signals.on_request.emit(request)

    async def on_response(self, response):
        await self._signals.on_response.emit(response)

    async def on_processed_response(self, result):
        await self._signals.on_processed_response.emit(result)

    async def on_request_error(self, error, request):
        await self._signals.on_request_error.emit(error, request)

    async def on_response_process_error(self, error, response):
        await self._signals.on_response_process_error.emit(error, response)