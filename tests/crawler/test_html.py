import pytest
from unisul_sync_gui.crawler import html
from aiohttp.test_utils import (
    make_mocked_coro, 
)

from unittest.mock import Mock

fake_document = '''
<html id='html'>
    <body id='test'>bar</body>
</html>
'''


@pytest.mark.asyncio
async def test_html_parser_xpath():
    response = Mock()
    response.text = make_mocked_coro(fake_document)

    parser = await html.parse(response)
    result = parser.xpath('.')

    assert len(result) == 1


@pytest.mark.asyncio
async def test_item_loader_with_valid_xpaths():
    expected = 'foo'

    response = Mock()
    response.text = make_mocked_coro(fake_document)

    parser = await html.parse(response)
    builder = html.ItemBuilder(dict, parser)

    builder.add_xpath(expected, './/*[@id="test"]')
    result = builder.build()

    assert isinstance(result, dict) and \
            result[expected] == 'bar'


@pytest.mark.asyncio
async def test_item_loader_with_many_keys():
    expecteds = ['foo', 'bar']
    response = Mock()
    response.text = make_mocked_coro(fake_document)

    parser = await html.parse(response)
    builder = html.ItemBuilder(dict, parser)

    for key in expecteds:
        builder.add_xpath(key, './/*[@id="test"]')

    result = builder.build()

    assert list(result) == expecteds


@pytest.mark.asyncio
async def test_item_loader_with_not_valid_xpaths():
    response = Mock()
    response.text = make_mocked_coro(fake_document)

    parser = await html.parse(response)
    builder = html.ItemBuilder(dict, parser)

    with pytest.raises(ValueError):
        builder.add_xpath('foo', './/*[@id="not-exist"]')

