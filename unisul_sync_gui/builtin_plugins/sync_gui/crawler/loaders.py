from .items import Subject, Book
from ....crawler import abc


class SubjectLoader(abc.AbstractItemLoader):
    def xpath_tree(self, response):
        return '//div[@id="grad"]/div[1]/div[1]/div[1]/div'

    def item_factory(self, **kwargs):
        return Subject(**kwargs)

    def fill(self, builder):
        builder.add_xpath('class_id', './/a/@data-turma_id')
        builder.add_xpath('name', './/p/text()')

    def is_valid(self, item: Subject) -> bool:
        return item.class_id and item.name


class BookLoader(abc.AbstractItemLoader):
    def __init__(self, subject: Subject):
        self.subject = subject

    def xpath_tree(self, response):
        return '//div[@id="insereEspaco"]/div'
    
    def item_factory(self, **kwargs):
        return Book(**kwargs)

    def fill(self, builder):
        builder.add_xpath('name', './/small//text()')

        url_xpath = './/a[@title="Download" or @title="Acessar"]/@href'
        builder.add_xpath('download_url', url_xpath)

        builder.add_value('subject', self.subject)

    def is_valid(self, item: Book) -> bool:
        return item.name and item.download_url


class LearningUnitBookLoader(BookLoader):
    def xpath_tree(self, response):
        return '//*[@id="tituloGrad"]/following-sibling::div/div'
