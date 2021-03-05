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

    def parse_subjects(self, response, request):
        pass


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