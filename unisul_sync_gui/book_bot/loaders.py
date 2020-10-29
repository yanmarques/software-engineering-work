from .items import Subject, Book, MaxSubject, MaxBook, first_when_list
from unisul_sync_gui.book_bot.utils import http
from scrapy.loader import ItemLoader
from scrapy.http import Response

from urllib.parse import urljoin, parse_qs
from scrapy.utils.url import urlparse


def ensure_has_return(item, *args):
    for value in list(args) + ['name']:
        if not value in item:
            return None
    return item


def join_url(base_url):
    def processor(value):
        return urljoin(base_url, first_when_list(value))
    return processor


class UrlAwareLoader(ItemLoader):
    def __init__(self, url, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.download_url_out = join_url(url)


class SubjectLoader:
    def get_tree(self, response: Response):
        return response.xpath("//div[@id='grad']/div[1]/div[1]/div[1]/div")

    @staticmethod
    def from_dict(data: dict):
        return Subject(name=data['name'], class_id=data['class_id'])

    def __call__(self, subject_tree):
        loader = ItemLoader(item=Subject(), selector=subject_tree)
        loader.add_xpath('class_id', './/a/@data-turma_id')
        loader.add_xpath('name', './/p/text()')
        return ensure_has_return(loader.load_item(), 'class_id')


class BookLoader:
    def __init__(self, subject: Subject):
        self.subject = subject

    def get_tree(self, response: Response):
        return response.xpath("//div[@id='insereEspaco']/div")

    def set_fallback_filename(self, book):
        book['filename'] = book['name']

    def parse_filename(self, book):
        parsed_url = urlparse(book['download_url'])
        link_hostname = parsed_url.hostname

        # is this an random internet link?
        if link_hostname and link_hostname != http.EVA_DOMAIN:
            self.set_fallback_filename(book)
            return book

        parsed_qs = parse_qs(parsed_url.query)
    
        if Book.qs_file_arg in parsed_qs:
            book['filename'] = parsed_qs[Book.qs_file_arg][0]
            return book

        def on_download_headers(response):
            try:
                default_filename = http.urljoin(http.EVA_BASE_URL, 
                                                book['download_url'])
                filename = http.parse_filename(response, default_filename)
                book['filename'] = filename
            except FileNotFoundError:
                self.set_fallback_filename(book)
            return book

        # we do not have the name yet
        # so let's find it
        return http.web_open(book['download_url'], 
                             callback=on_download_headers,
                             method='HEAD')

    @staticmethod
    def from_dict(data: dict):
        subject = SubjectLoader.from_dict(data['subject'])
        return Book(name=data['name'], 
                    download_url=data['download_url'], 
                    filename=data['filename'],
                    subject=subject)

    def __call__(self, book_tree):
        loader = ItemLoader(item=Book(), selector=book_tree)
        loader.add_xpath('name', './/small//text()')
        loader.add_xpath('download_url', './/a[@title="Download"]/@href')
        loaded_book = loader.load_item()
        loaded_book['subject'] = self.subject
        book = ensure_has_return(loaded_book, 'download_url')
        if book:
            print(f'subj: {self.subject} book: {book}')
            return self.parse_filename(book)


class LearningUnitBookLoader(BookLoader):
    def get_tree(self, response: Response):
        return response.xpath("//*[@id='tituloGrad']/following-sibling::div/div")

    
class MaxSubjectLoader(SubjectLoader):
    def get_tree(self, response):
        night_subjects = response.xpath('//table[2]/tbody[1]/tr[last()]/td')
        del night_subjects[0]
        return night_subjects
    
    @staticmethod
    def from_dict(data):
        return MaxSubject(name=data['name'], url=data['url'])

    def __call__(self, subject_tree):
        loader = ItemLoader(item=MaxSubject(), selector=subject_tree)
        loader.add_xpath('url', './/a[1]/@href')
        loader.add_xpath('name', './/text()')
        return ensure_has_return(loader.load_item(), 'url')


class MaxBookLoader(BookLoader):
    def get_tree(self, response):
        books = response.xpath('/html/body/table/tbody/tr')
        if len(books):
            del books[0]
        return books

    @staticmethod
    def from_dict(data: dict):
        subject = MaxSubjectLoader.from_dict(data['subject'])
        return MaxBook(name=data['name'], 
                        download_url=data['download_url'], 
                        filename=data['filename'],
                        subject=subject)

    def __call__(self, book_tree):
        item = MaxBook(subject=self.subject)
        loader = ItemLoader(item=item, selector=book_tree)
        link_xpath = './/td[last()]/a[1]'
        loader.add_xpath('download_url', f'{link_xpath}/@href')
        loader.add_xpath('name', f'{link_xpath}/text()')
        return ensure_has_return(loader.load_item(), 'download_url')