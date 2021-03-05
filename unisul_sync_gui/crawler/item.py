import functools
import dataclasses
from typing import Any


class Text(str):
    '''
    Subclass used to recognize fields with default processor.
    '''


class field(dataclasses.Field):
    def __init__(self, 
                 input_processor,
                 *args,
                 **kwargs) -> None:
        '''
        Allows passing dataclasses field values through functions. 
        '''

        _field = dataclasses.field(*args, **kwargs)
        super().__init__(_field.default, 
                         _field.default_factory, 
                         _field.init, 
                         _field.repr, 
                         _field.hash, 
                         _field.compare,
                         _field.metadata)
        self.process_input = input_processor

    
class PipeCompose:
    def __init__(self, *args) -> None:
        '''
        Aggregate the list of functions into a simple call.
        '''

        self.fns = args

    def __call__(self, value: Any) -> Any:
        reducer = lambda v, fn: fn(v) or v
        return functools.reduce(reducer, self.fns, value)


class Item:
    def __post_init__(self):
        '''
        Process each field through configured processors.
        '''

        for field in dataclasses.fields(self):
            print(field)
            # dummy processor that returns what is passed
            processor = lambda v: v

            if hasattr(field, 'process_input') and field.process_input:
                processor = field.process_input
            elif field.type is Text:
                processor = text_processor()

            print(processor)
            original_value = getattr(self, field.name)
            output = processor(original_value)
            setattr(self, field.name, output)


def text_processor(*args):
    '''
    Return nice default text processors.
    '''

    return PipeCompose(str, *args, str.strip, remove_crlf)


def remove_crlf(value: Text):
    '''
    Remove carrige return and line fields.

    value: Input text.
    '''

    return value.strip('\r\n')