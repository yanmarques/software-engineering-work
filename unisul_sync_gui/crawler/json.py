from . import abc

import json


class JsonDumper(abc.IODumper):
    def write_fp(self, fp, data, **kwargs):
        kwargs.setdefault('indent', 2)
        return json.dump(data, fp, **kwargs)

    def read_fp(self, fp, **kwargs):
        return json.load(fp, **kwargs)


class JsonExporter(abc.ListExporter):
    def dumper_factory(self, path):
        return JsonDumper(path)