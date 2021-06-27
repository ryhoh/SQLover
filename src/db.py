import os
from typing import List, Tuple, Union

import psycopg2
import psycopg2.errors


DATABASE = os.environ.get('DATABASE_URL') or 'postgresql://web:web@localhost:54321/sqlabo'


def read_JWT_secret() -> str:
    """
    Read JWT secret

    :return: JWT secret
    """
    with psycopg2.connect(DATABASE) as conn:
        with conn.cursor() as cur:
            cur.execute("select value from credential where type = 'JWT_secret';")
            res: List[str] = cur.fetchone()
            return res[0]


def create_user(username: str, password: bytes, email: str) -> bool:
    """
    Create new user

    :param username: new user's name
    :param password: new user's password (hashed)
    :param email: new user's email address
    :return: True if successfully created else False
    """
    with psycopg2.connect(DATABASE) as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    insert into users(name, passwd, email)
                    values(%s, %s, %s);
                """, (username, password, email))
        except psycopg2.errors.UniqueViolation:
            return False
        finally:
            conn.commit()
    return True


def read_user_from_user(name: str) -> Tuple[bytes, str, bool]:
    """
    Read user's password

    :param name: user's name
    :return: (hashed password, email, is_active)
    """
    with psycopg2.connect(DATABASE) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                select passwd, email, is_active
                from users
                where name = %s;
            """, (name,))

            res: List[Union[memoryview, str, bool]] = cur.fetchone()
            if res is None:
                raise ValueError("User not exist:", name)
    return res[0].tobytes(), res[1], res[2]


def read_username_from_user_by_email(email: str) -> str:
    """
    Read user's name by email.

    :param email: user's email
    :return: username
    """
    with psycopg2.connect(DATABASE) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                select name
                from users
                where email = %s;
            """, (email,))

            res: List[str] = cur.fetchone()
            if res is None:
                raise ValueError("User not exist with email:", email)
    return res[0]


def update_users_active(user_name: str):
    """
    Update user's availability.

    (Called after verification of new user)

    :param user_name: user's name
    :return: Number of cleared
    """
    with psycopg2.connect(DATABASE) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                update users
                set is_active = true
                where name = %s;
            """, (user_name,))
        conn.commit()


def update_users_password(user_name: str, password: bytes):
    """
    Change user's password

    :param user_name: username to change password
    :param password: new password
    """
    with psycopg2.connect(DATABASE) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                update users
                set passwd = %s
                where name = %s;
            """, (password, user_name))
            conn.commit()


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


def read_cleared_problem_from_result(user_name: str) -> List[Tuple[str]]:
    """
    Read an user's problems of cleared.

    :param user_name: user's name
    :return: Problem names of cleared
    """
    with psycopg2.connect(DATABASE) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                select problems.name
                from results
                join problems on results.problem_id = problems.id
                where results.cleared and results.user_id = (
                    select users.id from users
                    where users.name = %s
                );
            """, (user_name,))
            res: List[Tuple[str]] = cur.fetchall()
    return res


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
        return False  # We currently treat AC and WA (We don't record PE).

    with psycopg2.connect(DATABASE) as conn:
        with conn.cursor() as cur:
            # Once cleared, results.cleared never get back to false.
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
                update set cleared = (results.cleared or %s);
            """, (problem_name, user_name, (category == 'AC'), (category == 'AC')))
        conn.commit()
    return True


def delete_inactivated_users():
    """
    Delete all users who is not activated.

    """
    with psycopg2.connect(DATABASE) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                delete
                from users
                where is_active = false;
            """)
        conn.commit()
