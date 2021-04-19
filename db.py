import os
from typing import List

import psycopg2
import psycopg2.errors


DATABASE = os.environ.get('DATABASE_URL') or 'postgresql://web:web@localhost/sqlabo'


def create_user(name: str, password: bytes) -> bool:
    """
    Create new user

    :param name: new user's name
    :param password: new user's password (hashed)
    :return: True if successfully created else False
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


def read_passwd_by_name_from_user(name: str) -> bytes:
    """
    Read user's password

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


def create_problem(name: str) -> bool:
    """
    Create new problem

    :param name: name of new problem
    :return: True if successfully created else False
    """
    with psycopg2.connect(DATABASE) as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    insert into problems(name)
                    values(%s);
                """, (name,))
        except psycopg2.errors.UniqueViolation:
            return False
        finally:
            conn.commit()
    return True


def read_cleared_num_from_result(user_name: str) -> int:
    """
    Count an user's number of cleared.

    :param user_name: user's name
    :return: Number of cleared
    """
    with psycopg2.connect(DATABASE) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                select sum(cleared::int) from results
                where user_id = (select id from users
                    where users.name = %s)
                group by user_id;
            """, (user_name,))
            res: List[int] = cur.fetchone()
            if res is None:
                return 0  # Nothing cleared yet
    return res[0]


def upsert_result(problem_name: str, user_name: str, category: str) -> bool:
    """
    Update or Insert new result

    :param problem_name: name of problem
    :param user_name: user's name
    :param category: "AC", "WA", "PE", ...
    :return: True if successfully created else False
    """
    if category not in ('AC', 'WA'):
        return False

    with psycopg2.connect(DATABASE) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                insert into results(problem_id, user_id, cleared)
                values(
                    (select problems.id from problems
                    where problems.name = %s),
                    (select users.id from users
                    where users.name = %s),
                    %s
                )
                on conflict on constraint results_problem_id_user_id_un do
                update set cleared = %s;
            """, (problem_name, user_name, (category == 'AC'), (category == 'AC')))
        conn.commit()
    return True

