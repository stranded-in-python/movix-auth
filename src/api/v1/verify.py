from fastapi import APIRouter, Body, Depends, HTTPException, Request, status
from pydantic import EmailStr

import core.exceptions as exceptions
from api import schemas
from api.v1.common import ErrorCode, ErrorModel
from db import models_protocol
from managers.user import BaseUserManager, UserManagerDependency


def get_verify_router(
    get_user_manager: UserManagerDependency[
        models_protocol.UP,
        models_protocol.SIHE,
        models_protocol.OAP,
        models_protocol.UOAP,
    ],
    user_schema: type[schemas.U],
):
    router = APIRouter()

    @router.post(
        "/request-verify-token",
        status_code=status.HTTP_202_ACCEPTED,
        name="verify:request-token",
    )
    async def request_verify_token(
        request: Request,
        email: EmailStr = Body(..., embed=True),
        user_manager: BaseUserManager[
            models_protocol.UP,
            models_protocol.SIHE,
            models_protocol.OAP,
            models_protocol.UOAP,
        ] = Depends(get_user_manager),
    ):
        try:
            user = await user_manager.get_by_email(email)
            await user_manager.request_verify(user, request)
        except (
            exceptions.UserNotExists,
            exceptions.UserInactive,
            exceptions.UserAlreadyVerified,
        ):
            pass

        return None

    @router.post(
        "/verify",
        response_model=user_schema,
        name="verify:verify",
        responses={
            status.HTTP_400_BAD_REQUEST: {
                "model": ErrorModel,
                "content": {
                    "application/json": {
                        "examples": {
                            ErrorCode.VERIFY_USER_BAD_TOKEN: {
                                "summary": "Bad token, not existing user or"
                                "not the e-mail currently set for the user.",
                                "value": {"detail": ErrorCode.VERIFY_USER_BAD_TOKEN},
                            },
                            ErrorCode.VERIFY_USER_ALREADY_VERIFIED: {
                                "summary": "The user is already verified.",
                                "value": {
                                    "detail": ErrorCode.VERIFY_USER_ALREADY_VERIFIED
                                },
                            },
                        }
                    }
                },
            }
        },
    )
    async def verify(
        request: Request,
        token: str = Body(..., embed=True),
        user_manager: BaseUserManager[
            models_protocol.UP,
            models_protocol.SIHE,
            models_protocol.OAP,
            models_protocol.UOAP,
        ] = Depends(get_user_manager),
    ):
        try:
            user = await user_manager.verify(token, request)
            return user_schema.from_orm(user)

        except (exceptions.InvalidVerifyToken, exceptions.UserNotExists):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.VERIFY_USER_BAD_TOKEN,
            )
        except exceptions.UserAlreadyVerified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.VERIFY_USER_ALREADY_VERIFIED,
            )

    return router
