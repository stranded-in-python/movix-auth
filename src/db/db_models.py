import uuid

from database import Base
from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import TIMESTAMP, UUID
from sqlalchemy.orm import relationship


class Role(Base):
    __tablename__ = 'role'

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    name = Column(String, nullable=False)

    user_role = relationship("UserRole", back_populates="roles")

    def __repr__(self):
        return f'<Role {self.id} : {self.name}>'


class UserSensitive(Base):
    __tablename__ = 'sensitive'

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    password = Column(String, nullable=False)

    user_role = relationship("UserRole", back_populates="users")
    user_history = relationship("SignInHistory", back_populates="users")

    def __repr__(self):
        return f'<User {self.username}>'


class UserRole(Base):
    __tablename__ = 'user_role'

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("sensitive.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    role_id = Column(
        UUID(as_uuid=True), ForeignKey("role.id", onupdate="CASCADE"), nullable=False
    )

    users = relationship("UserSensitive", back_populates="items")
    roles = relationship("Role", back_populates="user_role")

    def __repr__(self):
        return f'<UserRole {self.user_id} : {self.role_id}>'


class SignInHistory(Base):
    __tablename__ = 'sign_in_history'

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("sensitive.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    user_agent = Column(String, nullable=False)
    sign_in_at = Column(TIMESTAMP(timezone=True), nullable=False)

    users = relationship("UserSensitive", back_populates="user_history")
    refresh_tokens = relationship("RefreshToken", back_populates="sessions")

    def __repr__(self):
        return f'<SignInHistory: {self.user_id} at {self.sign_in_at} from {self.user_agent}'


class RefreshToken(Base):
    __tablename__ = 'sessions'

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("sign_in_history.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )

    sessions = relationship("SignInHistory", back_populates="refresh_tokens")
