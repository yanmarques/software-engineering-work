import pytest
from unisul_sync_gui.builtin_plugins.sync_gui.crawler import (
    items,
    loaders,
)
from aiohttp.test_utils import make_mocked_coro

import os
from unittest.mock import Mock


def get_test_html(filename):
    cwd = os.path.dirname(os.path.abspath(os.path.realpath(__file__)))
    with open(os.path.join(cwd, filename), 'r') as io_r:
        return io_r.read()


def response_from(filename):
    content = get_test_html(filename)
    response = Mock()
    response.text = make_mocked_coro(content)
    return response


@pytest.mark.asyncio
async def test_subject_parser_load_items(middleware_factory, mock_crawler_session):
    expected = [
        items.Subject(name='Foo', class_id='123'),
        items.Subject(name='Bar', class_id='321'),
        items.Subject(name='Baz', class_id='213'),
    ]
    
    response = response_from('subject-spider-response.html')

    result = await loaders.SubjectLoader().load(response)

    assert result == expected


@pytest.mark.asyncio
async def test_book_load_items(middleware_factory, mock_crawler_session):
    subject = Mock()

    expected = [
        items.Book(name='Book 1', 
                   download_url='/foo', 
                   filename=None,
                   is_external=False,
                   seems_downloadable=False,
                   subject=subject),
        items.Book(name='Book 2', 
                   download_url='/bar?arquivo=test-filename',
                   filename='test-filename',
                   is_external=False,
                   seems_downloadable=True,
                   subject=subject),
        items.Book(name='Book 3',
                   download_url='https://www.fake.com',
                   filename=None,
                   is_external=True,
                   seems_downloadable=False,
                   subject=subject),
    ]
    
    response = response_from('book-spider-response.html')

    result = await loaders.BookLoader(subject).load(response)

    assert result == expected