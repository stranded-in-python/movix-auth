from fastapi import APIRouter, Depends, HTTPException, Request, status

import models as m
import schemas as schemas
import core.exceptions as ex
from services.abc import BaseUserService
from services.user import get_user_service
from api.v1.common import ErrorCode, ErrorModel

router = APIRouter()


@router.post(
    "/register",
    response_model=m.UserRegistrationParamsOut,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Register a new user in Movix-Auth service",
    response_description="Short representation of created user",
    tags=['Register'],
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorModel,
            "content": {
                "application/json": {
                    "examples": {
                        ErrorCode.REGISTER_USER_ALREADY_EXISTS: {
                            "summary": "A user with this email already exists.",
                            "value": {
                                "detail": ErrorCode.REGISTER_USER_ALREADY_EXISTS
                            },
                        },
                        ErrorCode.REGISTER_INVALID_PASSWORD: {
                            "summary": "Password validation failed.",
                            "value": {
                                "detail": {
                                    "code": ErrorCode.REGISTER_INVALID_PASSWORD,
                                    "reason": "Password should be"
                                    "at least 8 characters",
                                }
                            },
                        },
                    }
                }
            },
        },
    }
)
async def register(
    request: Request,
    user_create: schemas.UC,
    user_service: BaseUserService = Depends(get_user_service)
) -> schemas.U:
    try:
        created_user = await user_service.create(
            user_create, safe=True, request=request
        )
    except ex.UserAlreadyExists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.REGISTER_USER_ALREADY_EXISTS,
        )
    except ex.InvalidPasswordException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": ErrorCode.REGISTER_INVALID_PASSWORD,
                "reason": e.reason,
            },
        )

    return user_create.from_orm(created_user)

