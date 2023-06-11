import os
from contextlib import closing

import psycopg2

from core.password.password import PasswordHelper

dsl = {'dbname': os.getenv('POSTGRES_DB'), 'user': os.getenv('POSTGRES_USER'),
    'password': os.getenv('POSTGRES_PASSWORD'), 'host': os.getenv('POSTGRES_HOST'), 
    'port': os.getenv('POSTGRES_PORT')}

password_hasher = PasswordHelper()

superuser_password = repr(password_hasher.hash(os.getenv('SUPER_USER_PW')))[1:-1]
superuser_id = repr(os.getenv('SUPER_USER_ID'))[1:-1]
superuser_login = repr(os.getenv('SUPER_USER_LOGIN'))[1:-1]
superuser_email = repr(os.getenv('SUPER_USER_EMAIL'))[1:-1]

if __name__ == '__main__':
    with closing(psycopg2.connect(**dsl)) as pg_conn:
        curs = pg_conn.cursor()
        curs.execute(f"""
            INSERT INTO users.user (id, username, email, hashed_password, is_active, is_superuser, first_name, last_name)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
            (id, username, email, hashed_password, is_active, is_superuser, first_name, last_name) 
            = (EXCLUDED.id, EXCLUDED.username, EXCLUDED.email, EXCLUDED.hashed_password, EXCLUDED.is_active, EXCLUDED.is_superuser, EXCLUDED.first_name, EXCLUDED.last_name);
        """, (superuser_id, superuser_login, superuser_email, superuser_password, True, True, "super", "user"))
        pg_conn.commit()
