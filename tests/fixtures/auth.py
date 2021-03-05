import pytest
from unisul_sync_gui import auth


@pytest.fixture
def logged_on_eva():
    auth_service = auth.Authenticator()
    if not auth_service.logged:
        auth_service.try_from_disk()
        raise auth.AuthenticationException()

    return auth_service._session
