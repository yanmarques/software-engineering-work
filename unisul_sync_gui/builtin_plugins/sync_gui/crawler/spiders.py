from typing import List
from unisul_sync_gui.builtin_plugins.sync_gui.crawler.items import Subject
from . import loaders
from ....crawler import (
    http,
    EVASpiderMixin,
)


class SubjectSpider(EVASpiderMixin, http.RequestLoaderMixin):
    subject_args = dict(turmaIdSessao=-1,
                        situacao="C",
                        turmaId=-1,
                        disciplinaId=-1,
                        confirmacao=0,
                        subMenu="",
                        ferramenta="")

    def start_requests(self):
        yield self.request(url='/listaDisciplina.processa',
                           params=self.subject_args, 
                           loader=loaders.SubjectLoader())


class BookSpider(EVASpiderMixin, http.RequestLoaderMixin):
    book_params = dict(situacao=1,
                       tipoFiltro=0,
                       turmaAberta='true',
                       turmaFechada='false')

    def __init__(self, subjects: List[Subject]):
        super().__init__()
        self.subjects = subjects

    def start_requests(self):
        for subject in self.subjects:
            # get query parameters for this subject
            params = self._get_book_params(subject)

            # reguler books
            yield self.request(url='/listaMidiatecas.processa', 
                               params=params,
                               loader=loaders.BookLoader(subject))

            # learning unit books
            yield self.request(url='/listaMidiateca.processa', 
                               params={'turmaIdSessao': subject.class_id},
                               loader=loaders.LearningUnitBookLoader(subject))
    
    def _get_book_params(self, subject: Subject):
        new_params = self.book_params.copy()
        new_params['turmaIdSessao'] = subject.class_id
        return new_params


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