from abc import ABC, abstractmethod


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
        self.items = None
        self.item = None

    @abstractmethod
    def dumper_factory(self, *args, **kwargs):
        pass

    @abstractmethod
    def should_export(self):
        pass

    @abstractmethod
    def reset_exported_items(self):
        pass

    @abstractmethod
    def add_item_to_export_list(self):
        pass

    def done_to_export(self):
        return True

    def export(self, items, **kwargs):
        self.reset_exported_items()

        self.items = items

        for item in self.items:
            self.item = item
            if self.should_export():
                self.add_item_to_export_list()
        
        if self.done_to_export():
            self.dumper.dump(self.exported_items, **kwargs)


class ListExporter(BaseExporter):
    '''
    Keep items to dumps as a list.
    '''
    
    def reset_exported_items(self):
        self.exported_items = []

    def add_item_to_export_list(self):
        self.exported_items.append(self.item)
