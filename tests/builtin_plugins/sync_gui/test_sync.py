from unisul_sync_gui.crawler import (
    signal, 
    cookie,
    MiddlewareAwareCrawler,
)
from unisul_sync_gui.builtin_plugins.sync_gui.crawler import (
    exporter,
    spiders,
)


async def implementation():
    async def on_subjects_done(subjects):
        e = exporter.SubjectExporter('test-subjects.json')
        e.export(subjects)
        subjects = e.dumper.load()

    s = signal.CrawlerSignals()
    s.on_processed_response.connect(on_subjects_done)

    m = signal.SignalingMiddleware(spiders.SubjectSpider(), s)

    def session_factory():
        return cookie.ClientSession('foo.cookie')

    c = MiddlewareAwareCrawler(m, session_factory=session_factory)
    c.start()