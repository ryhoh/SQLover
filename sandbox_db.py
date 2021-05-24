import os
import psycopg2
import psycopg2.extras
from typing import List, Tuple, Dict, Any, Union


SANDBOX_DB = os.environ.get('SANDBOX_DB_URL') or 'postgresql://web:web@localhost:54320/sandbox'
BAD_WORDS = frozenset({
    'create', 'update', 'insert', 'delete', 'drop', 'alter', 'insert', 'database', 'role', 'grant', 'set',
    'definition', 'database', 'table', 'current_user', 'pg_user', 'current_schema', 'pg_roles',
})


class Result:
    def __init__(
            self,
            has_error: bool,
            error_message: str = None,
            columns: List[str] = None,
            records: List[Tuple[Any]] = None
    ):
        self.has_error = has_error
        self.error_message = error_message
        self.columns = columns
        self.records = records


class IllegalCommandError(Exception):
    pass


def read_version() -> str:
    """
    Read the version of PostgreSQL

    :return: Version information
    """
    with psycopg2.connect(SANDBOX_DB) as conn:
        with conn.cursor() as cur:
            cur.execute("select version();")
            return cur.fetchone()[0]


def sanitize(query: str) -> str:
    """
    Check and modify submitted query and return runnable sql.

    - Find illegal command
    - Extract one (first) sentence

    :param query: Submitted query
    :return: Runnable sql
    """
    to_check: str = query.split(';')[0].lower()
    for bad_word in BAD_WORDS:
        if bad_word in to_check:
            raise IllegalCommandError('[App] Illegal command: %s' % bad_word)
    return query.split(';')[0]


def execute(
        ddl: Union[str, List[str]],
        tables: List[Dict[str, Any]],
        query: str
) -> Result:
    """
    独立した sqlite3 データベース上で，テーブル作成とクエリを実行する

    :param ddl: テーブル作成に用いる DDL
    :param tables: insert する，(テーブルの名前，レコードなどの辞書)の配列
    :param query: 実行するクエリ
    :return: 実行結果
    """
    # todo docstringを英語化
    with psycopg2.connect(SANDBOX_DB) as conn:
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                # Make tables
                if isinstance(ddl, str):
                    cur.execute(ddl)
                elif '__iter__' in dir(ddl):
                    for statement in ''.join(ddl).split(';'):
                        if statement == '':
                            continue
                        cur.execute(statement + ';')  # Execute each SINGLE statement
                else:
                    raise ValueError("Illegal DDL. DDL must be str or iterable.")

                # Insert records
                for table in tables:
                    for record in table['records']:
                        val = '(' + ','.join(
                            "'" + elm + "'" if isinstance(elm, str) else str(elm)
                            for elm in record
                        ) + ')'
                        cur.execute("insert into %s values %s" % (table['name'], val))

                # Test query
                query = sanitize(query)
                cur.execute(query)  # Don't care sql-injection because this is an independent DB.
                result_columns = [col.name for col in cur.description]
                result_records = cur.fetchall()
        except (psycopg2.ProgrammingError, IllegalCommandError) as e:
            return Result(has_error=True, error_message=str(e))
        finally:  # prepare for next
            conn.rollback()

    result_records = [tuple(record) for record in result_records]
    return Result(has_error=False, columns=result_columns, records=result_records)
