from unisul_sync_gui.crawler import item

import dataclasses
from unittest.mock import Mock


@dataclasses.dataclass
class FakeItem(item.Item):
    name: item.Text


def custom_item_factory(input_processor):
    @dataclasses.dataclass
    class FakeItem(item.Item):
        name: str = item.field(
            input_processor=input_processor
        )

    return FakeItem


def test_default_text_field_processor():
    expected = 'foo'

    result = FakeItem(name=f'    \rfoo\n\r\n   ')
    assert result.name == expected


def test_field_custom_processor():
    expected = 'foo'

    def processor(value):
        assert value == 'bar'
        return expected

    result = custom_item_factory(processor)(name='bar')

    assert result.name == expected


def test_pipe_compose_puts_output_of_function_on_next_function_input():
    expected = 'foo'

    def processor1(_):
        return 'ignored'

    def processor2(value):
        assert value == 'ignored'
        return expected

    pipe = item.PipeCompose(processor1, processor2)

    result = custom_item_factory(pipe)(name='bar')

    assert result.name == expected