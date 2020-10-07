from . import cookies, config, spider
from .book_bot.utils import http
from .app import context
from .book_bot.spiders import eva_auth

import os
import json
import stat


class _names:
    username = 'id_login'
    password = 'id_senha'


class AuthenticationException(Exception):
    def __init__(self, message='User is not authenticated.', **kwargs):
        super().__init__(message, **kwargs)


class Authenticator:
    def __init__(self):
        self._session = context.http_session
        self.logged = False
        if cookies.try_cookie_from_disk():
            # lets try these cookies
            if check_response(self._session.get(http.EVA_BASE_URL)):
                self.logged = True

    def with_creds(self, username, password, rememberme=None):
        creds_payload = {_names.username: username,
                        _names.password: password} 

        url = http.EVA_BASE_URL.strip('/') + '/login.processa'
        response = self._session.post(url, data=creds_payload)
        if check_response(response):
            # housekeeping
            cookies.extract_to_file()
            if rememberme:
                dump_keys(username, password)
            return self._set_status(True)
        return self._set_status(False)

    def try_from_disk(self):
        if not os.path.exists(auth_name()):
            return self._set_status(False)

        with open(auth_name(), encoding='utf8') as io_reader:
            auth_data = json.load(io_reader).values()

            # stop here if we got an unexpected format
            if len(auth_data) != 2:
                return self._set_status(False)

        return self.with_creds(*auth_data)

    def logout(self):
        result = spider.crawl(eva_auth.LogoutSpider)
        if result is not None:
            print(result)

    def _set_status(self, status):
        self.logged = status
        return status


def check_response(response):
    if response.history and response.history[-1].status_code != 302:
        return True

    body = response.text
    has_ids = _names.username in body and _names.password in body
    has_js_redirect = 'eadv4/login/index.jsp' in body
    return not (has_ids or has_js_redirect)


def dump_keys(username, password):
    with open(auth_name(), 'w', encoding='utf8') as io_writer:
        json.dump({'username': username, 'password': password}, io_writer, indent=4)
    os.chmod(auth_name(), 0o600)


def auth_name():
    return config.path_name_of('auth.json')