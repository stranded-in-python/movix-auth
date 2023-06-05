# from typing import Generic, Sequence, Type

# import db.models_protocol as models
# from api.v1.rights import APIRouter, get_access_rights_router
# from authentication import AuthenticationBackend, Authenticator
# from managers.rights import AccessRightManagerDependency
# from managers.role import RoleManagerDependency
# from managers.user import UserManagerDependency

# RoleMgrDependencyType = RoleManagerDependency[
#     models.RP, models.URUP
# ]
# AccessRightMgrDependencyType = AccessRightManagerDependency[
#     models.ARP, models.RARP, models.RARUP, models.ID
# ]


# class APIAccessRight(
#     Generic[
#         models.UP,
#         models.UC,
#         models.SIHE,
#         models.UU,
#         models.R,
#         models.UR,
#         models.URU,
#         models.AR,
#         models.ARC,
#         models.ARU,
#         models.RAR,
#         models.RARU,
#         models.ID,
#     ]
# ):
#     authenticator: Authenticator

#     def __init__(
#         self,
#         get_user_manager: UserManagerDependency[
#             models.U, models.SIHE
#         ],
#         get_role_manager: RoleManagerDependency[
#             models.R, models.UR, models.RC, models.RU, models.URU
#         ],
#         get_access_rights_manager: AccessRightManagerDependency[
#             models.AR,
#             models.ARC,
#             models.ARU,
#             models.RAR,
#             models.RARU,
#             models.ID,
#         ],
#         auth_backends: Sequence[AuthenticationBackend],
#     ):
#         self.get_user_manager = get_user_manager
#         self.get_role_manager = get_role_manager
#         self.get_access_rights_manager = get_access_rights_manager
#         self.authenticator = Authenticator(auth_backends, get_user_manager)
#         self.current_user = self.authenticator.current_user

#     def get_access_rights_router(
#         self,
#         access_right_schema: Type[models.AR],
#         access_right_create_schema: Type[models.ARC],
#         access_right_update_schema: Type[models.ARU],
#         role_access_right_schema: Type[models.RAR],
#         role_access_right_update_schema: Type[models.RARU],
#         id_schema: Type[models.ID],
#     ) -> APIRouter:
#         return get_access_rights_router(
#             self.get_user_manager,
#             self.get_role_manager,
#             self.get_access_rights_manager,
#             access_right_schema,
#             access_right_create_schema,
#             access_right_update_schema,
#             role_access_right_schema,
#             role_access_right_update_schema,
#             id_schema,
#             self.authenticator,
#         )
