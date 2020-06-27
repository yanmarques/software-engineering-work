from getpass import getpass

import scrapy
from unisul_sync_gui.book_bot.items import maybe_getattr
from unisul_sync_gui.book_bot.utils import http, os_files


def check_login(fn):
    def wrapper(cls, response):
        if LoginSpider.auth_failed(response):
            raise AuthenticationException()
        return fn(cls, response)
    return wrapper


def interative_login(fn):
    def wrapper(cls, retry):
        def interative_wrapper(response):
            try:
                return check_login(fn)(cls, response)
            except AuthenticationException as e:
                return retry(response)
        return interative_wrapper
    return wrapper


def get_credentials(io_reader=None, username=None):
    if io_reader:
        with io_reader as h:
            username, password = h.readlines()
    else:
        header = 'Username'
        if username:
            header += f' [{username}]'
        header += ': '
        username, password = input(header), getpass()
    return username.strip(), password.strip()


class AuthenticationException(Exception):
    def __init__(self, message='User is not authenticated.', **kwargs):
        super().__init__(message, **kwargs)


class LoginSpider(scrapy.Spider):
    name = 'eva_login'
    allowed_domains = http.EVA_DOMAIN

    # Cli arguments
    authentication_file = 'auth_file'

    # Request information
    username_arg = 'id_login'
    password_arg = 'id_senha'

    __auth_fake__ = False

    def start_requests(self):
        yield http.web_open(callback=self.get_login_handler())

    @interative_login
    @http.log_request
    def after_login(self, response):
        self.logger.info('logged in')

    def retry_login(self, response):
        self.logger.info('authentication failed')
        
        original_data = response.meta.get('creds', None)
        if original_data:
            del response.meta['creds']
            self._log_user(original_data, 'last login with username: %s')
        
        self.logger.info('retrying login...')
        new_credentials = self._read_auth(default_dict=original_data)

        self._log_user(new_credentials, 'login attempt with user: %s')
        yield http.web_open('/login.processa',
                            callback=self.get_login_handler(),
                            formdata=new_credentials,
                            meta={'creds': new_credentials},
                            dont_filter=True,
                            impl=scrapy.FormRequest)
    
    def get_login_handler(self):
        return self.after_login(self.retry_login)

    @staticmethod
    def auth_failed(response):
        # fake authentication...bad?
        if LoginSpider.__auth_fake__:
            LoginSpider.__auth_fake__ = False
            return False

        body = response.body

        # text is bytes-like object
        user_key = LoginSpider.username_arg.encode()
        pwd_key = LoginSpider.password_arg.encode()
        has_ids = user_key in body and pwd_key in body
        has_js_redirect = b'eadv4/login/index.jsp' in body

        if 'redirect_reasons' in response.meta:
            redirect_statuses = response.meta['redirect_reasons']
            if redirect_statuses and redirect_statuses[-1] != 302:
                return False
        return has_ids or has_js_redirect
    
    @staticmethod
    def fake_auth():
        LoginSpider.__auth_fake__ = True

    def _build_creds(self, username, password, default_username=None):
        if not username and default_username:
            username = default_username
        return {LoginSpider.username_arg: username,
                LoginSpider.password_arg: password} 

    def _read_auth(self, default_dict=None):
        auth_file = maybe_getattr(self, LoginSpider.authentication_file)
        if auth_file:
            auth_file = open(auth_file, 'r')
        
        username = None
        if default_dict is not None and LoginSpider.username_arg in default_dict:
            username = default_dict[LoginSpider.username_arg]
        
        args = get_credentials(io_reader=auth_file, username=username)
        return self._build_creds(*args, default_username=username)

    def _log_user(self, formdata, message):
        if LoginSpider.username_arg in formdata:
            self.logger.info(message, formdata[LoginSpider.username_arg])


class LogoutSpider(scrapy.Spider):
    name = 'logout_eva'
    allowed_domains = http.EVA_DOMAIN

    def start_requests(self):
        yield http.web_open(callback=self.parse_home)

    def parse_home(self, response):
        logout_url = response.css('#icon-sair-perfil').xpath('.//following::a[1]/@href').get()
        if logout_url:
            return http.web_open(logout_url, callback=self.handle_exit)
        self.logger.debug('user already out!?')

    @http.log_request
    def handle_exit(self, response):
        self.logger.debug('logout redirects: %s', response.meta)
        self.logger.info('logged out')