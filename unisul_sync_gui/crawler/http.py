from . import abc

import os
from urllib.parse import urlparse


class Request(abc.objectview):
    def __init__(self, **kwargs):
        '''
        Represents a http request object.

        url: Relative url of web request.
        callback: Required keyword argument.
        **kwargs: Other arguments used when calling request.
        '''
        super().__init__(**kwargs)

        if 'url' not in self.to_dict():
            raise ValueError('Missing "url" parameter')

        if 'callback' not in self.to_dict():
            raise ValueError('Missing "callback" parameter')
            
        # default http method: GET
        self.setdefault('method', 'GET')

    def parse_url(self, spider: abc.Spider):
        '''
        Transform the url according to spider settings.
        '''

        parse = urlparse(self.url)

        # relative urls
        if parse.netloc == '':
            if spider.domain is None:
                raise ValueError('Spider has no default domain')

            # set spider domain and scheme
            kwargs = dict(netloc=spider.domain,
                        scheme=spider.scheme)

            # needs a path preffix
            if spider.preffix is not None:
                preffixed_path = os.path.join(spider.preffix,
                                            parse.path.lstrip('/'))
                kwargs.update(path=preffixed_path)

            # fix url
            parse = parse._replace(**kwargs)

        return parse.geturl()