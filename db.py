import os
from typing import List

import psycopg2
import psycopg2.errors


DATABASE = os.environ.get('DATABASE') or 'postgresql://web:web@localhost/sqlabo'


def get_passwd_by_name_from_user(name: str) -> bytes:
    """
    Load user's password

    :param name: user's name
    :return: hashed password
    """
    with psycopg2.connect(DATABASE) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                select passwd
                from users
                where name = %s;
            """, (name,))

            res: List[memoryview] = cur.fetchone()
            if res is None:
                raise ValueError("User not exist:", name)
    return res[0].tobytes()  # get single value


def user_register(name: str, password: bytes) -> bool:
    """
    Register new user

    :param name: new user's name
    :param password: new user's password (hashed)
    :return: True if successfully registered else False
    """
    with psycopg2.connect(DATABASE) as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    insert into users(name, passwd)
                    values(%s, %s);
                """, (name, password))
        except psycopg2.errors.UniqueViolation:
            return False
        finally:
            conn.commit()

    return True
