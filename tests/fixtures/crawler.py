import pytest
from unisul_sync_gui.crawler import (
    abc, 
    json, 
    http,
    AsyncCrawler,
)
from aiohttp.test_utils import make_mocked_coro

from pathlib import Path
from unittest.mock import Mock

fake_document = '''
<html>
    <body>
        <div id='1'>foo</div>

        <div id='2'>bar</div>

        <div id='3'>baz</div>
    </body>
</html>
'''


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
        if isinstance(requests, http.Request):
            requests = [requests]
        self.requests = requests

    def start_requests(self):
        for request in self.requests:
            yield request


class FakeContext:
    def __init__(self, **kwargs) -> None:
        pass

    async def __aenter__(self):
        return Mock()

    def __aexit__(self, *_):
        return self

    def __await__(self):
        yield


class FakeMiddleware(abc.Middleware):
    async def on_request(self, request):
        pass

    async def on_response(self, response):
        pass

    async def on_request_error(self, error, request):
        pass

    async def on_response_process_error(self, error, response):
        pass

    async def on_processed_response(self, result):
        pass


class FakeDocumentLoader(abc.AbstractItemLoader):
    def xpath_tree(self, response) -> str:
        return './/body/div'

    def fill(self, builder) -> None:
        builder.add_xpath('test', './text()')

    def is_valid(self, item) -> bool:
        return True

    def item_factory(self, **kwargs):
        return dict(**kwargs)


@pytest.fixture
def fake_response():
    response = Mock()
    response.text = make_mocked_coro(fake_document)
    return response


@pytest.fixture
def fake_loader(fake_response):
    loader = FakeDocumentLoader()
    old_fn = loader.load
    load_patch = lambda *_, **__: old_fn(fake_response)
    loader.load = load_patch
    return loader


@pytest.fixture
def middleware_factory():
    return FakeMiddleware


@pytest.fixture
def fake_middleware(middleware_factory, fake_spider):
    return middleware_factory(fake_spider)


@pytest.fixture
def fake_spider(spider_factory):
    request = http.Request(url='/', 
                           callback=make_mocked_coro())
    return spider_factory(request)


@pytest.fixture
def assert_crawl_urls(spider_factory, crawler_factory):
    def wrapper(expected, inputs=None):
        inputs = inputs or expected
        results = []

        async def test_request(_, request):
            results.append(request.url)

        def workers():
            for i in inputs:
                yield http.Request(url=i, callback=test_request)

        spider = spider_factory(workers())

        runner = crawler_factory(spider)
        runner.start()

        assert results == expected
    return wrapper


@pytest.fixture
def spider_factory():
    return FakeSpider


@pytest.fixture
def mock_crawler_session():
    def wrapper(crawler, mock=FakeContext):
        old_http_req = crawler._http_req
            
        async def _http_req(_, session, __):
            session.request = mock
            await old_http_req(_, session, __)

        crawler._http_req = _http_req
        return crawler
    return wrapper


@pytest.fixture
def crawler_factory(mock_crawler_session):
    def wrapper(spider):
        crawler = AsyncCrawler(spider)
        return mock_crawler_session(crawler)
        
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
