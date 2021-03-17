import pytest
from unisul_sync_gui.crawler import auth
from aiohttp.test_utils import make_mocked_coro
from aiohttp import CookieJar

from unittest.mock import Mock, MagicMock


@pytest.mark.asyncio
async def test_auth_success_from_disk_creds(successfull_auth, fake_ctx_factory):
    expected = {
        successfull_auth.user_field: 'foo',
        successfull_auth.passwd_field: 'bar',
    }

    def ensure_params(*args, data=None, **kwargs):
        assert data == expected
        return fake_ctx_factory()

    mock = Mock(side_effect=ensure_params)

    successfull_auth._request = mock

    await successfull_auth.from_rememberme()

    mock.assert_called()
    assert successfull_auth.is_logged_in is True


@pytest.mark.asyncio
async def test_auth_from_creds_return_login_status(successfull_auth):
    result = await successfull_auth.from_rememberme()
    assert result is True and result == successfull_auth.is_logged_in


@pytest.mark.asyncio
async def test_auth_with_failed_check_response(auth_manager):
    mock = make_mocked_coro(False)
    auth_manager.check_response = mock

    await auth_manager.from_rememberme()

    mock.assert_called()
    assert auth_manager.is_logged_in is False


@pytest.mark.asyncio
async def test_auth_succeeded_when_not_redirected(mock_auth_manager):
    mock_response = Mock()
    history = Mock()
    history.status = 200
    mock_response.history = [history]

    auth_manager = mock_auth_manager(mock_response)

    await auth_manager.from_rememberme()

    assert auth_manager.is_logged_in is True


@pytest.mark.asyncio
async def test_auth_check_response_last_history(mock_auth_manager):
    ignored_history = Mock()
    ignored_history.status = 302

    history = Mock()
    history.status = 200

    mock_response = Mock()
    mock_response.history = [ignored_history, history]

    auth_manager = mock_auth_manager(mock_response)

    await auth_manager.from_rememberme()

    assert auth_manager.is_logged_in is True


@pytest.mark.asyncio
async def test_auth_succeeded_when_302_with_no_js_redirect(mock_auth_manager):
    mock_response = Mock()
    history = Mock()
    history.status = 302
    mock_response.history = [history]

    mock_response.text = make_mocked_coro('')
    auth_manager = mock_auth_manager(mock_response)

    await auth_manager.from_rememberme()

    assert auth_manager.is_logged_in is True


@pytest.mark.asyncio
async def test_auth_failed_with_custom_html(with_js_redirect_response):
    await with_js_redirect_response.from_rememberme()

    assert with_js_redirect_response.is_logged_in is False


@pytest.mark.asyncio
async def test_successfull_auth_from_creds_save_to_disk(successfull_auth: auth.AsyncAuthManager):
    expected_creds = ('foo', 'bar')

    await successfull_auth.from_creds(*expected_creds)
    
    result = successfull_auth.load_creds()

    assert result == expected_creds


@pytest.mark.asyncio
async def test_auth_loads_and_saves_cookies_with_ctx_manager(successfull_auth: auth.AsyncAuthManager):
    # initialize a cookie in disk
    cookie_jar = CookieJar()
    cookie_jar.update_cookies(dict(foo='bar'))
    cookie_jar.save(successfull_auth._session.cookies_path)

    # run object using context manager
    async with successfull_auth:
        pass

    session = successfull_auth._session
    assert session.cookie_jar._cookies['']['foo'].value == 'bar'
    