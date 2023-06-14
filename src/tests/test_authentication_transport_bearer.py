import pytest
from fastapi import status
from fastapi.responses import JSONResponse

from authentication.transport import BearerTransport, TransportLogoutNotSupportedError
from authentication.transport.bearer import BearerResponse

pytestmark = pytest.mark.asyncio

@pytest.fixture()
def bearer_transport() -> BearerTransport:
    return BearerTransport(token_url="/login")


@pytest.mark.authentication
async def test_get_login_response(bearer_transport: BearerTransport):
    response = await bearer_transport.get_login_response("TOKEN")

    assert isinstance(response, JSONResponse)
    assert response.body == b'{"access_token":"TOKEN","token_type":"bearer"}'


@pytest.mark.authentication
async def test_get_logout_response(bearer_transport: BearerTransport):
    with pytest.raises(TransportLogoutNotSupportedError):
        await bearer_transport.get_logout_response()


@pytest.mark.authentication
@pytest.mark.openapi
def test_get_openapi_login_responses_success(bearer_transport: BearerTransport):
    openapi_responses = bearer_transport.get_openapi_login_responses_success()
    assert openapi_responses[status.HTTP_200_OK]["model"] == BearerResponse


@pytest.mark.authentication
@pytest.mark.openapi
def test_get_openapi_logout_responses_success(bearer_transport: BearerTransport):
    openapi_responses = bearer_transport.get_openapi_logout_responses_success()
    assert openapi_responses == {}
