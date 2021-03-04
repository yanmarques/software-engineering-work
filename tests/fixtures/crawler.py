import pytest
from unisul_sync_gui.crawler import abc, json, AsyncRunner

from pathlib import Path


class FakeDumper(abc.IODumper):
    def write_fp(self, fp, data, **kwargs):
        pass

    def read_fp(self, fp, **kwargs):
        pass


class FakeExporter(abc.ListExporter):
    def dumper_factory(self, path):
        return FakeDumper(path)
    
    def should_export(self, item):
        return True


class FakeSpider(abc.Spider):
    domain = 'www.fake.com'

    def __init__(self, requests) -> None:
        super().__init__()
        if isinstance(requests, abc.Request):
            requests = [requests]
        self.requests = requests

    def start_requests(self):
        for request in self.requests:
            yield request


class FakeContext:
    def __init__(self, **kwargs) -> None:
        pass

    def __aenter__(self):
        return self

    def __aexit__(self, *_):
        return self

    def __await__(self):
        yield


@pytest.fixture
def assert_crawl_urls(spider_factory, crawler_factory):
    def wrapper(expected, inputs=None):
        inputs = inputs or expected
        results = []

        def test_request(_, request):
            results.append(request.url)

        def workers():
            for i in inputs:
                yield abc.Request(url=i, callback=test_request)

        spider = spider_factory(workers())

        runner = crawler_factory(spider)
        runner.start()

        assert results == expected
    return wrapper


@pytest.fixture
def spider_factory():
    return FakeSpider


@pytest.fixture
def crawler_factory():
    def wrapper(spider):
        runner = AsyncRunner(spider)
        old_http_req = runner._http_req
        
        async def _http_req(_, session, __):
            session.request = FakeContext
            await old_http_req(_, session, __)

        runner._http_req = _http_req
        return runner
    return wrapper


@pytest.fixture
def json_dumper(tmp_path):
    file_path = tmp_path / Path('out')
    dumper = json.JsonDumper(file_path)
    return dumper


@pytest.fixture
def fake_exporter(tmp_path):
    file_path = tmp_path / Path('out')
    fake_exp = FakeExporter(file_path)
    return fake_exp


@pytest.fixture
def mock_exporter_write(fake_exporter):
    def wrapper(mock):
        fake_exporter.dumper.write_fp = mock
        return fake_exporter

    return wrapper


@pytest.fixture
def exp_write_args(mock_exporter_write):
    return mock_exporter_write(lambda _, *args, **__: args)


@pytest.fixture
def exp_write_kwargs(mock_exporter_write):
    return mock_exporter_write(lambda *_, **kwargs: kwargs)
