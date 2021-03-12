from typing import Any, Coroutine
from pydispatch import dispatcher 
from aiohttp.signals import Signal


class pysignal:
    def emit(self, 
             sender=dispatcher.Any,
             *args, 
             **kwargs):
        dispatcher.send(signal=self, 
                        sender=sender, 
                        *args, 
                        **kwargs)

    def connect(self, *args, **kwargs):
        dispatcher.connect(*args, signal=self, **kwargs)

    
class AsyncPysignal:
    def __init__(self) -> None:
        self._store = Signal(None)

    async def emit(self, *args, **kwargs):
        self._store.freeze()
        await self._store.send(*args, **kwargs)

    def connect(self, listener: Coroutine):
        self._store.append(listener)


class _signals:
    # app life cycle
    opening = pysignal()
    closing = pysignal()
    started = pysignal()

    auth_done = pysignal()
    auth_failed = pysignal()

    showing = pysignal()
    shown = pysignal()

    landing = pysignal()
    landed = pysignal()
