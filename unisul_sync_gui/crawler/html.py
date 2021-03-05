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

    def add_xpath(self, 
                  key, 
                  xpath, 
                  default=None,
                  raises=False):
        '''
        Adds a value from the given xpath.

        If found value is empty and ``raises`` is false, uses 
        ``default`` as value, it raises a ``ValueError`` if 
        ``raises`` is true though.
        '''

        el = self.parser.xpath(xpath)
        if not el and raises:
            raise ValueError(f'Provided xpath returned empty: {xpath}')
        
        if el:
            value = el[0]
        else:
            value = default

        self.add_value(key, value)

    def add_value(self, key, value):
        '''
        Adds ``value`` to be built on the key ``key``.
        '''

        self._params[key] = value

    def build(self):
        '''
        Call factory and return created object with added parameters.
        '''

        return self.factory(**self._params)

