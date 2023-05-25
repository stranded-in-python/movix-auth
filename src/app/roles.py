from api.roles import APIRoles

api_roles = APIRoles[User, UUID](get_user_manager, [auth_backend])