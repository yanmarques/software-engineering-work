import pytest
from . import crawler
from unisul_sync_gui.crawler import auth
from aiohttp.test_utils import make_mocked_coro

from unittest.mock import Mock
from pathlib import Path


js_redirect_response = '''
<html>
    <head>
    </head>
    <body>
        <script type="text/javascript">
            window.location.href = "/eadv4/login/index.jsp?turmaId=-1&ferramenta=&subMenu=&id=-1";
    </script>
    </body>
</html>
'''


class FakeAuthManager(auth.AsyncAuthManager):
    def load_creds(self):
        return ('foo', 'bar')


@pytest.fixture
@pytest.mark.asyncio
async def auth_manager(tmp_path, fake_ctx_factory):
    manager = FakeAuthManager(tmp_path / Path('foo-creds'), 
                              tmp_path / Path('foo-cookies'))

    manager._request = lambda *_, **__: fake_ctx_factory()
    yield manager
    await manager.close()


@pytest.fixture
def successfull_auth(auth_manager):
    auth_manager.check_response = make_mocked_coro(True)
    return auth_manager


@pytest.fixture
def mock_auth_manager(auth_manager, fake_ctx_factory):
    def wrapper(response):
        auth_manager._request = lambda *_, **__: \
                                fake_ctx_factory(return_value=response)

        return auth_manager

    return wrapper


@pytest.fixture
def with_js_redirect_response(mock_auth_manager):
    response = Mock()

    # ignore history
    response.history = None

    response.text = make_mocked_coro(js_redirect_response)
    auth_manager = mock_auth_manager(response)
    return auth_manager
