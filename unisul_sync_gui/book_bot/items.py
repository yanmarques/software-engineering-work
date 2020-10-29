# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
import os
from urllib.parse import parse_qs, unquote

import scrapy
from unisul_sync_gui.book_bot.utils import http
from scrapy.utils.url import urlparse
from scrapy.loader.processors import MapCompose, TakeFirst
from scrapy.selector.unified import Selector
from scrapy.item import Item
from scrapy.loader import ItemLoader


def default_field(*args):
    input_proc = MapCompose(first_when_list, parse_tree, str, *args, str.strip, remove_bad_chars)
    return scrapy.Field(
        input_processor=input_proc,
        output_processor=TakeFirst()
    )


def remove_bad_chars(value):
    return ' '.join(value.replace("\r\n", '').split())


def parse_tree(value):
    if isinstance(value, Selector):
        return value.get()
    return value


def first_when_list(value):
    if isinstance(value, list):
        return TakeFirst()(value)
    return value


def parse_subject_name(name):
    fragments = name.split('-')

    # TODO does this cover all cases?
    if 'AOL' in fragments[0]:
        return fragments[-1]
    return fragments[-2]


def maybe_getattr(cls, name, default=None):
    if hasattr(cls, name):
        return getattr(cls, name)
    return default


class NamedItem(Item):
    name = default_field()

    def __str__(self):
        return self['name']


class Subject(NamedItem):
    name = default_field(parse_subject_name)
    class_id = default_field()


class Book(NamedItem):
    download_url = default_field()
    filename = default_field(unquote)
    subject = scrapy.Field()

    qs_file_arg = 'arquivo'

    @property
    def path(self):
        media_name = self['filename']
        media_dir = self['subject']['name']
        return os.path.join(media_dir, media_name)


class MaxSubject(NamedItem):
    url = default_field()


class MaxBook(Book):
    def parse_filename(self):
        self.set_filename(os.path.basename(self['download_url']))
        

    