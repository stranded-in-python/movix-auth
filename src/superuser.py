import os
from contextlib import contextmanager, closing

import psycopg2
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor

from core.password.password import PasswordHelper

dsl = {'dbname': os.getenv('POSTGRES_DB'), 'user': os.getenv('POSTGRES_USER'),
    'password': os.getenv('POSTGRES_PASSWORD'), 'host': os.getenv('POSTGRES_HOST'), 
    'port': os.getenv('POSTGRES_PORT')}

# dsl = {'dbname': os.getenv('POSTGRES_DB'), 'user': os.getenv('POSTGRES_USER'),
#      'password': os.getenv('POSTGRES_PASSWORD'), 'host': "localhost", 
#      'port': 5434}


password_hasher = PasswordHelper()

superuser_password = password_hasher.hash(os.getenv('SUPER_USER_PW'))
superuser_id = os.getenv('SUPER_USER_ID')


if __name__ == '__main__':
    with closing(psycopg2.connect(**dsl)) as pg_conn:
        curs = pg_conn.cursor()
        curs.execute(f"""
            INSERT INTO users.user (id, username, email, hashed_password, is_active, is_superuser, first_name, last_name)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
            (id, username, email, hashed_password, is_active, is_superuser, first_name, last_name) 
            = (EXCLUDED.id, EXCLUDED.username, EXCLUDED.email, EXCLUDED.hashed_password, EXCLUDED.is_active, EXCLUDED.is_superuser, EXCLUDED.first_name, EXCLUDED.last_name);
        """, (superuser_id, "superuser", "superuser@movix.com", superuser_password, True, True, "super", "user"))
        pg_conn.commit()
