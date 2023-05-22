import uuid
from sqlalchemy.orm import mapped_column
from sqlalchemy.schema import ForeignKey
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP

from db import db


class TableMixin(db.Model):
    __table_args__ = {'schema': 'users'}


class Role(TableMixin):
    __tablename__ = 'role'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    name = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f'<Role {self.id} : {self.name}>'


class UserSensitive(TableMixin):
    __tablename__ = 'sensitive'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'
    

class UserRole(TableMixin):
    __tablename__ = 'user_role'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = db.Column(UUID(as_uuid=True), ForeignKey("sensitive.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    role_id = db.Column(UUID(as_uuid=True), ForeignKey("role.id", onupdate="CASCADE"), nullable=False)

    def __repr__(self):
        return f'<UserRole {self.user_id} : {self.role_id}>'
    

class SignInHistory(TableMixin):
    __tablename__ = 'sign_in_history'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = db.Column(UUID(as_uuid=True), ForeignKey("sensitive.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    user_agent = db.Column(db.String, nullable=False)
    sign_in_at = mapped_column(TIMESTAMP(timezone=True), nullable=False)

    def __repr__(self):
        return f'<SignInHistory: {self.user_id} at {self.sign_in_at} from {self.user_agent}'
    

class RefreshToken(TableMixin):
    __tablename__ = 'sessions'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    session_id = db.Column(UUID(as_uuid=True), ForeignKey("sign_in_history.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)