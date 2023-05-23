from http import HTTPStatus
from uuid import UUID

from flask import request
from injector import inject

from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource
from pydantic import ValidationError

import src.models.models as m
from src.services.abc import BaseUserService


class UserResource(Resource):
    @inject
    def __init__(self, user_service: BaseUserService):
        self.user_service = user_service

    @jwt_required()
    def get(self):
        current_user = m.UserPayload(id=get_jwt_identity()) # Получить из payload идентификатор

        return self.user_service.get(current_user.id)\
                                .json()

    @jwt_required()
    def put(self):
        request_data = request.get_json()

        try:
            user = m.UserUpdateIn(**request_data)

        except ValidationError as e:
            return {'message': 'Validation errors', 'errors': e},\
                   HTTPStatus.BAD_REQUEST

        return self.user_service.put(user)

