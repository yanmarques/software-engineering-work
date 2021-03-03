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
    
    @abstractmethod
    def write_fp(self, fp, data, **kwargs):
        pass

    def dump(self, data, **kwargs):
        encoding = kwargs.get('encoding', 'utf-8')
        with open(self.path, 'w', encoding=encoding) as fp:
            self.write_fp(fp, data, **kwargs)


class BaseExporter(ABC):
    def __init__(self,
                 dumper: IODumper):
        '''
        Export manager with a generic processing function.

        dumper: Implementation handles sending output to a file.
        '''

        super().__init__()

        self.dumper = dumper

        # hold valid items to export
        self.exported_items = None

        # parameters received on export() function
        self.items = None
        self.item = None

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
