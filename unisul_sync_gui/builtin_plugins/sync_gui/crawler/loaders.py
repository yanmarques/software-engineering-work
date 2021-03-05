from .items import Subject, Book
from aiohttp.web import Response

from urllib.parse import parse_qs, urlparse


def ensure_has_return(item, *args):
    for value in list(args) + ['name']:
        if not value in item:
            return None
    return item


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

    def finish_parsing(self, book):
        # default is not downloadable
        book['seems_downloadable'] = False

        parsed_url = urlparse(book['download_url'])
        link_hostname = parsed_url.hostname

        # is this an random internet link?
        if link_hostname and link_hostname != http.EVA_DOMAIN:
            book['is_external'] = True
        else:
            book['is_external'] = False

            # try to retrieve filename from url
            parsed_qs = parse_qs(parsed_url.query)
            if Book.qs_file_arg in parsed_qs:
                book['filename'] = parsed_qs[Book.qs_file_arg][0]

                # assume it is always downloadable 
                book['seems_downloadable'] = True
                return book

        # deduce which base url of the request
        if book['is_external']:
            # means no base url, the download_url attribute
            # is already a full url
            base_url = ''
        else:
            base_url = http.EVA_BASE_URL

        def on_download_headers(response):
            default_filename = http.urljoin(base_url, 
                                            book['download_url'])
            filename = None

            try:
                filename = http.parse_filename(response)
                if filename:
                    book['seems_downloadable'] = True
            except FileNotFoundError:
                pass

            book['filename'] = filename or default_filename
            return book

        # we do not have the name yet
        # so let's find it
        return http.web_open(book['download_url'],
                             base_url=base_url, 
                             callback=on_download_headers,
                             method='HEAD')

    @staticmethod
    def from_dict(data: dict):
        subject = SubjectLoader.from_dict(data['subject'])
        return Book(name=data['name'], 
                    download_url=data['download_url'], 
                    filename=data['filename'],
                    is_external=data['is_external'],
                    seems_downloadable=data['seems_downloadable'],
                    subject=subject)

    def __call__(self, book_tree):
        loader = ItemLoader(item=Book(), selector=book_tree)
        loader.add_xpath('name', './/small//text()')

        url_xpath = './/a[@title="Download" or @title="Acessar"]/@href'
        loader.add_xpath('download_url', url_xpath)

        loaded_book = loader.load_item()
        loaded_book['subject'] = self.subject
        book = ensure_has_return(loaded_book, 'download_url')
        if book:
            return self.finish_parsing(book)


class LearningUnitBookLoader(BookLoader):
    def get_tree(self, response: Response):
        return response.xpath("//*[@id='tituloGrad']/following-sibling::div/div")

