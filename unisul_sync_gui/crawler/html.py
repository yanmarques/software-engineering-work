from lxml import html
from aiohttp.web import Response


async def parse(response: Response) -> html.HtmlElement:
    '''
    Returns a feature rich html parser from response content.

    response: Http response received from a request.
    '''

    content = await response.text()
    return html.document_fromstring(content)


class ItemBuilder:
    def __init__(self, factory, parser: html.HtmlElement) -> None:
        '''
        Helps building an object from html element paths.

        factory: Callable that creates an item.
        parser: Source of information.
        '''

        self.factory = factory
        self.parser = parser
        self._params = {}

    def add_xpath(self, key, xpath):
        el = self.parser.xpath(xpath)
        if not el:
            raise ValueError(f'Provided xpath returned empty: {xpath}')
        
        value = el[0].text_content()
        self.add_value(key, value)

    def add_value(self, key, value):
        self._params[key] = value

    def build(self):
        return self.factory(**self._params)

