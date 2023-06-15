import os
from contextlib import closing

import psycopg2

from core.password.password import PasswordHelper

dsl = {
    'dbname': os.getenv('POSTGRES_DB'),
    'user': os.getenv('POSTGRES_USER'),
    'password': os.getenv('POSTGRES_PASSWORD'),
    'host': os.getenv('POSTGRES_HOST'),
    'port': os.getenv('POSTGRES_PORT'),
}


password_hasher = PasswordHelper()

superuser_password = password_hasher.hash(os.getenv('SUPER_USER_PW', 'qweasd123'))
superuser_id = os.getenv('SUPER_USER_ID', '90cb9877-c9fe-466a-9ba6-0505b2931779')
superuser_login = os.getenv('SUPER_USER_LOGIN', 'superuser')
superuser_email = os.getenv('SUPER_USER_EMAIL', 'superuser@movix.com')

if __name__ == '__main__':
    with closing(psycopg2.connect(**dsl)) as pg_conn:
        curs = pg_conn.cursor()
        query = """
            INSERT INTO users.user (id, username, email, hashed_password, is_active, is_superuser, first_name, last_name)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
            (id, username, email, hashed_password, is_active, is_superuser, first_name, last_name)
            = (EXCLUDED.id, EXCLUDED.username, EXCLUDED.email, EXCLUDED.hashed_password, EXCLUDED.is_active, EXCLUDED.is_superuser, EXCLUDED.first_name, EXCLUDED.last_name);
        """
        values = (
            superuser_id,
            superuser_login,
            superuser_email,
            superuser_password,
            True,
            True,
            "super",
            "user",
        )
        curs.execute(curs.mogrify(query, values))
        pg_conn.commit()
