from ....crawler import html
from aiohttp.web import Response

from abc import ABC, abstractmethod


class AbstractItemLoader(ABC):
    '''
    Receives a web response and returns a list of items
    to be further processed.
    '''

    @abstractmethod
    def xpath_tree(self, response: Response) -> str:
        '''
        Returns the xpath to the tree of elements.
        '''

        pass

    @abstractmethod
    def fill(self, builder: html.ItemBuilder) -> None:
        '''
        Use the buider to put informations when later
        creating the item.

        builder: Object to help creating items from html elements.
        '''

        pass

    @abstractmethod
    def is_valid(self, item) -> bool:
        '''
        Deduces whether item is valid to be sent.

        item: Item built with ``html.ItemBuilder``.
        '''

        pass

    @abstractmethod
    def item_factory(self, **kwargs):
        '''
        Instantiates an item.

        kwargs: Parameters to create item.
        '''

        pass

    def process_item(self, item):
        '''
        The purpose of this method is to give total control
        over every item to the subclasses.

        item: Object that will be returned from load()
        '''

        return item

    async def load(self, response: Response) -> list:
        '''
        Load items from response.

        response: Response to get content from.
        '''

        # get class xpath
        xpath = self.xpath_tree(response)

        # instantiates object that do the hard work
        parser = await html.parse(response)

        # get our list
        fragment_tree = parser.xpath(xpath)

        if not fragment_tree:
            raise ValueError(f'Received empty tree for response: {response}')
        
        # hold every instantiated item
        items = []

        for element in fragment_tree:
            builder = html.ItemBuilder(self.item_factory, element)

            # let the class decide how to build the item
            self.fill(builder)

            # instantiate it to test whether it is valid
            item = builder.build()

            # post-process
            item = self.process_item(item)

            # should add item?
            if self.is_valid(item):
                items.append(item)

        return items