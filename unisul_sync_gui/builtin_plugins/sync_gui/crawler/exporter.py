from . import items
from ....crawler import json, item


class SubjectExporter(item.DtClassAsDictMixin, json.JsonExporter):
    def should_export(self, item: items.Subject):
        return item.name and item.class_id

    
class BookExporter(item.DtClassAsDictMixin, json.JsonExporter):
    def process_item(self, item: items.Book):
        # fix when subject is a list, weird
        if isinstance(item.subject, list):
            item.subject = item.subject[0]
        return super(item.DtClassAsDictMixin).process_item(item)

    def should_export(self, item: items.Book):
        return item.name and item.download_url and item.filename
