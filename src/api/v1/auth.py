from http import HTTPStatus

from flask_jwt_extended import jwt_required, get_jwt_identity
from pydantic import ValidationError

from flask import request
from flask_restful import Resource
from injector import inject

import src.models.models as m
from src.services.abc import BaseAuthService


class RegistrationResource(Resource):
    @inject
    def __init__(self, auth_service: BaseAuthService):
        self.auth_service = auth_service

    def post(self):
        """Register a new user"""
        request_data = request.get_json()

        try:
            registration_request = m.UserRegistrationParamsIn(**request_data)

        except ValidationError as e:
            return {'message': 'Validation errors', 'errors': e},\
                   HTTPStatus.BAD_REQUEST

        self.auth_service.register(registration_request)

        return {'message': f'User {registration_request.username} registered successfully'},\
            HTTPStatus.CREATED


class LoginResource(Resource):
    @inject
    def __init__(self, auth_service: BaseAuthService):
        self.auth_service = auth_service

    def post(self):
        """Login to the account"""

        request_data = request.get_json()

        try:
            login_request = m.LoginParamsIn(**request_data)

        except ValidationError as e:
            return {'message': 'Validation errors', 'errors': e}, \
                HTTPStatus.BAD_REQUEST

        login_response = self.auth_service.login(login_request)

        return login_response.json()


class LogoutResource(Resource):
    @inject
    def __init__(self, auth_service: BaseAuthService):
        self.auth_service = auth_service

    @jwt_required()
    def post(self):
        """Logout of the account"""
        current_user = m.UserPayload(get_jwt_identity())

        self.auth_service.logout(current_user)

        return {'message': 'Logout successful'}, HTTPStatus.NO_CONTENT
