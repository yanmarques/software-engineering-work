from abc import ABC, abstractmethod, abstractproperty
from typing import Any, Generator


class IODumper(ABC):
    def __init__(self, file_path) -> None:
        '''
        Write contents to opened file descriptor.

        file_path:  File output. Will be created when it not exists or 
        truncated when it doesn't. 
        '''

        super().__init__()
        self.path = file_path
        self.default_encoding = 'utf-8'
    
    @abstractmethod
    def write_fp(self, fp, data, **kwargs):
        pass

    @abstractmethod
    def read_fp(self, fp, **kwargs):
        pass

    def dump(self, data, **kwargs):
        write_cb = self.write_fp
        return self._open_with(write_cb, 'w', data, **kwargs)

    def load(self, **kwargs):
        read_cb = self.read_fp
        return self._open_with(read_cb, 'r', **kwargs)

    def _open_with(self, cb, mode, *args, **kwargs):
        encoding = kwargs.get('encoding', self.default_encoding)
        with open(self.path, mode, encoding=encoding) as fp:
            return cb(fp, *args, **kwargs)


class BaseExporter(ABC):
    def __init__(self,
                 *args,
                 dumper: IODumper = None,
                 **kwargs):
        '''
        Export manager with a generic processing function.

        dumper: Implementation handles sending output to a file.
        '''

        super().__init__()

        self.dumper = dumper or \
                      self.dumper_factory(*args, **kwargs)

        # hold valid items to export
        self.exported_items = None

        # parameters received on export() function
        self._items = None

    @abstractmethod
    def dumper_factory(self, *args, **kwargs):
        pass

    @abstractmethod
    def should_export(self, item):
        pass

    @abstractmethod
    def reset_exported_items(self):
        pass

    @abstractmethod
    def add_item_to_export_list(self, item):
        pass

    def done_to_export(self):
        return True

    def process_item(self, item) -> Any:
        return item

    def export(self, items, **kwargs):
        self.reset_exported_items()

        self._items = items

        for item in self._items:
            if self.should_export(item):
                item_result = self.process_item(item)
                self.add_item_to_export_list(item_result)
        
        if self.done_to_export():
            return self.dumper.dump(self.exported_items, 
                                    **kwargs)


class ListExporter(BaseExporter):
    '''
    Keep items to dumps as a list.
    '''
    
    def reset_exported_items(self):
        self.exported_items = []

    def add_item_to_export_list(self, item):
        self.exported_items.append(item)


class objectview(object):
    def __init__(self, **kwargs):
        self.__dict__ = kwargs

    def update(self, **kwargs):
        self.__dict__.update(**kwargs)

    def setdefault(self, key, value):
        self.__dict__.setdefault(key, value)

    def to_dict(self):
        return self.__dict__.copy()


class Spider(ABC):
    '''
    Spider represents the information needed to start a crawler.
    '''

    # Used for the crawler to resolve relative urls.
    domain = None

    # Used for the crawler to add a default path preffix.
    preffix = None

    # Used for the crawler to set a default url scheme.
    scheme = 'https'

    @abstractmethod
    def start_requests(self) -> Generator:
        pass
    

class Middleware(ABC):
    def __init__(self, spider: Spider) -> None:
        '''
        Hooks into crawler's execution.

        spider: Target spider that will be crawled.
        '''
        super().__init__()
        self.spider = spider

    @abstractmethod
    async def on_request(self, request):
        pass

    @abstractmethod
    async def on_response(self, response):
        pass

    @abstractmethod
    async def on_processed_response(self, result):
        pass

    @abstractmethod
    async def on_request_error(self, error, request):
        pass

    @abstractmethod
    async def on_response_process_error(self, error, response):
        pass