from api.roles import APIRoles

api_users = APIRoles[User, UUID](get_user_manager, [auth_backend])