import pytest
from unisul_sync_gui.builtin_plugins.sync_gui.crawler import abc
from aiohttp.test_utils import (
    make_mocked_coro, 
)

from unittest.mock import Mock

fake_document = '''
<html>
    <body>
        <div id='1'>foo</div>

        <div id='2'>bar</div>

        <div id='3'>baz</div>
    </body>
</html>
'''


class FakeDocumentLoader(abc.AbstractItemLoader):
    def xpath_tree(self, response) -> str:
        return './/body/div'

    def fill(self, builder) -> None:
        builder.add_xpath('test', './text()')

    def is_valid(self, item) -> bool:
        return True

    def item_factory(self, **kwargs):
        return dict(**kwargs)


@pytest.fixture
def fake_response():
    response = Mock()
    response.text = make_mocked_coro(fake_document)
    return response


@pytest.mark.asyncio
async def test_item_loader_with_all_items(fake_response):
    expected = [
        {'test': 'foo',},
        {'test': 'bar',},
        {'test': 'baz',},
    ]

    loader = FakeDocumentLoader()
    result = await loader.load(fake_response)

    assert result == expected


@pytest.mark.asyncio
async def test_item_loader_not_includes_invalid_item(fake_response):
    blacklist = ['foo']
    expected = [
        {'test': 'bar',},
        {'test': 'baz',},
    ]

    loader = FakeDocumentLoader()
    
    # apply blacklist
    loader.is_valid = lambda item: item['test'] not in blacklist

    result = await loader.load(fake_response)

    assert result == expected


@pytest.mark.asyncio
async def test_item_loader_process_item_completely_changes_items(fake_response):
    expected = [1, 2, 3]

    loader = FakeDocumentLoader()
    
    loader.process_item = Mock(side_effect=expected)

    result = await loader.load(fake_response)

    assert result == expected


@pytest.mark.asyncio
async def test_item_loader_fails_with_empty_xpath(fake_response):
    loader = FakeDocumentLoader()
    
    loader.xpath_tree = Mock(return_value='.//*[@id="not-exists"]')

    with pytest.raises(ValueError):
        await loader.load(fake_response)