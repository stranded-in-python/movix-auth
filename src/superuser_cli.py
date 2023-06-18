import os
import uuid
import typer
import psycopg2

from core.password.password import PasswordHelper
from contextlib import closing

dsl = {
    'dbname': os.getenv('POSTGRES_DB'),
    'user': os.getenv('POSTGRES_USER'),
    'password': os.getenv('POSTGRES_PASSWORD'),
    # 'host': os.getenv('POSTGRES_HOST'),
    # 'port': os.getenv('POSTGRES_PORT'),
    'host': 'localhost',
    'port': 5434
}

def create_super_user(pg_conn, superuser_login, superuser_email, superuser_password, superuser_fn, superuser_ln):
    superuser_id = str(uuid.uuid4())
    curs = pg_conn.cursor()
    query = """
        INSERT INTO users.user
        (
            id, username, email, hashed_password, is_active, is_superuser, is_admin,
            first_name, last_name
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
    """
    values = (
        superuser_id,
        superuser_login,
        superuser_email,
        superuser_password,
        True,
        True,
        True,
        superuser_fn,
        superuser_ln,
    )
    curs.execute(curs.mogrify(query, values))
    pg_conn.commit()


def main():
    """
    Create superuser.

    If y is typed in first prompt, superuser is created with default values (from env),
    otherwise - you are promted with values 
    """
    automatic = typer.prompt('Create superuser automatically? (y/n): ').lower().strip() == 'y'
    password_hasher = PasswordHelper()
    if automatic:
        superuser_login = os.getenv('SUPER_USER_LOGIN', 'superuser')
        superuser_email = os.getenv('SUPER_USER_EMAIL', 'superuser@movix.com')
        superuser_password = password_hasher.hash(os.getenv('SUPER_USER_PW', 'qweasd123'))
        superuser_fn = 'super'
        superuser_ln = 'user'
    else:
        superuser_login = typer.prompt('Superuser login: ')
        superuser_password = password_hasher.hash(typer.prompt('Superuser password: '))
        superuser_email = typer.prompt('Superuser email: ')
        superuser_fn = typer.prompt('Superuser first name: ')
        superuser_ln = typer.prompt('Superuser last name: ')
    superuser_attrs = {"superuser_login": superuser_login, "superuser_password": superuser_password, "superuser_email": superuser_email,
            "superuser_fn": superuser_fn, "superuser_ln": superuser_ln}
    
    with closing(psycopg2.connect(**dsl)) as pg_conn:
        create_super_user(pg_conn, **superuser_attrs)

if __name__ == "__main__":
    typer.run(main)
