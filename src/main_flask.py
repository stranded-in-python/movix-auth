from flask import Flask
from flask_jwt_extended import JWTManager
from flask_restful import Resource, Api
from flask_injector import FlaskInjector

from api.v1.user import UserResource
from db.db import init_db
from src.api.v1.auth import RegistrationResource, LoginResource
from src.services.abc import BaseAuthService, BaseUserService
from src.services.auth import AuthService
from src.services.user import UserService


def configure(binder):
    # Привязка класса сервиса к интерфейсу
    binder.bind(BaseUserService, to=UserService)
    binder.bind(BaseAuthService, to=AuthService)
    binder.bind(BaseAuthService, to=AuthService)


app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = "super-secret"  # Change this!

api_v1 = Api(app, prefix='/api/v1')
api_v1.add_resource(UserResource, '/user')
api_v1.add_resource(RegistrationResource, '/register')
api_v1.add_resource(LoginResource, '/login')

if __name__ == '__main__':
    FlaskInjector(app=app, modules=[configure])
    JWTManager(app)

    app.run()
