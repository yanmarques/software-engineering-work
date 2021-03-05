from . import loaders
from ....crawler import http, abc


class AbstractEvaSpider(abc.Spider):
    domain = 'www.uaberta.unisul.br'
    preffix = '/eadv4/'


class SubjectSpider(AbstractEvaSpider):
    subject_args = dict(turmaIdSessao=-1,
                        situacao="C",
                        turmaId=-1,
                        disciplinaId=-1,
                        confirmacao=0,
                        subMenu="",
                        ferramenta="")

    def start_requests(self):
        yield http.Request(url='/listaDisciplina.processa',
                           params=self.subject_args, 
                           callback=self.parse_subjects)

    async def parse_subjects(self, response, request):
        loader = loaders.SubjectLoader()
        return await loader.load(response)


class BookSpider:
    book_args = dict(situacao=1,
                     tipoFiltro=0,
                     turmaAberta='true',
                     turmaFechada='false')

    def __init__(self):
        pass

    # def start_requests(self):
    #     for item in self.load_subjects():
    #         subject = SubjectLoader.from_dict(item)
    #         self.logger.debug('reading subject: %s', subject['name'])
    #         args = self._get_book_args(subject)
    #         yield http.web_open('/listaMidiatecas.processa', 
    #                             meta={'subject': subject},
    #                             args=args,
    #                             callback=self.parse_books)

    #         # get learning unit books
    #         yield http.web_open('/listaMidiateca.processa', 
    #                             meta={'subject': subject},
    #                             args={'turmaIdSessao': args['turmaIdSessao']},
    #                             callback=self.parse_learning_unit_books)
            
    # def parse_learning_unit_books(self, response):
    #     assert 'subject' in response.meta, 'Main subject was not provided.'
    #     subject = response.meta['subject']
    #     self.logger.debug('subject: %s', subject)
    #     return _display_and_load(self, 
    #                             'book', 
    #                             response, 
    #                             LearningUnitBookLoader(subject=subject))

    # def parse_books(self, response):
    #     assert 'subject' in response.meta, 'Main subject was not provided.'
    #     subject = response.meta['subject']
    #     self.logger.debug('subject: %s', subject)
    #     return _display_and_load(self, 
    #                             'book', 
    #                             response, 
    #                             self.get_loader(subject))

    # def load_subjects(self):
    #     return os_files.load_sync_data(self.exporter_dir, self.subject_uri)

    # def get_loader(self, subject):
    #     return BookLoader(subject=subject)
    
    def _get_book_args(self, subject_item):
        new_args = BookSpider.book_args
        new_args['turmaIdSessao'] = subject_item['class_id']
        return new_args


class FinishBook:
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