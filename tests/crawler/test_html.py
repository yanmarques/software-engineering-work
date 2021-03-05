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
    loader = html.ItemLoader(dict, parser)

    loader.add_xpath(expected, './/*[@id="test"]')
    result = loader.load()

    assert isinstance(result, dict) and \
            result[expected] == 'bar'


@pytest.mark.asyncio
async def test_item_loader_with_not_valid_xpaths():
    response = Mock()
    response.text = make_mocked_coro(fake_document)

    parser = await html.parse(response)
    loader = html.ItemLoader(dict, parser)

    with pytest.raises(ValueError):
        loader.add_xpath('foo', './/*[@id="not-exist"]')

