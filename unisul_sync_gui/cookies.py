from .book_bot import settings
from .config import path_name_of
from .app import context
from requests.cookies import create_cookie
from scrapy.http.cookies import CookieJar
from scrapy.utils.project import data_path
from scrapy_cookies.settings import default_settings

import pickle
import os


def extract_to_file(session=context.http_session):
    scrapy_jar = CookieJar(policy=session.cookies.get_policy()) 
    for cookie in session.cookies:
        scrapy_jar.set_cookie(cookie)

    with open(cookie_name(), 'wb') as io_writer:
        # save it in a way scrapy_cookies can gather later on
        pickle.dump({None: scrapy_jar}, io_writer)
    os.chmod(cookie_name(), mode=0o600)


def load_cookie(session=context.http_session):
    # bring cookie from deads
    with open(cookie_name(), 'rb') as io_reader:
        scrapy_jar = pickle.load(io_reader)[None]

    for cookie in scrapy_jar.jar:
        session.cookies.set_cookie(cookie)


def try_cookie_from_disk(**kwargs):
    if os.path.exists(cookie_name()):
        load_cookie(**kwargs)
        return True
    return False


def cookie_name():
    return path_name_of('cookies')