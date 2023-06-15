import uuid

import pytest

from db.users import BaseUserDatabase
from tests.conftest import IDType, OAuthAccount, SignInModel, UserModel, UserOAuth


@pytest.mark.asyncio
@pytest.mark.db
async def test_not_implemented_methods(user: UserModel):
    base_user_db = BaseUserDatabase[
        UserModel, IDType, SignInModel, UserOAuth, OAuthAccount
    ]()

    with pytest.raises(NotImplementedError):
        await base_user_db.get(uuid.uuid4())

    with pytest.raises(NotImplementedError):
        await base_user_db.get_by_email("lancelot@camelot.bt")

    with pytest.raises(NotImplementedError):
        await base_user_db.create({})

    with pytest.raises(NotImplementedError):
        await base_user_db.update(user, {})

    with pytest.raises(NotImplementedError):
        await base_user_db.delete(user)
