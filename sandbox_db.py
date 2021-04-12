import os
import psycopg2
from typing import List, Dict, Tuple, Any, Union


SANDBOX_DB = os.environ.get('SANDBOX_DB')


def _connect():
    if SANDBOX_DB is None:  # for debugging
        return psycopg2.connect(host="localhost", port=54320, user="web", password="web", database="sandbox")
    else:
        return psycopg2.connect(SANDBOX_DB)


def execute(
        ddl: Union[str, List[str]],
        tables: List[Dict[str, Any]],
        query: str
) -> List[Tuple[Any, ...]]:
    """
    独立した sqlite3 データベース上で，テーブル作成とクエリを実行する

    :param ddl: テーブル作成に用いる DDL
    :param tables: (テーブルの名前，レコードなどの辞書)の配列
    :param query: 実行するクエリ
    :return: クエリ結果
    """
    # todo docstringを英語化
    with _connect() as conn:
        with conn.cursor() as cur:
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
                    # Don't care sql-injection because this is an independent DB.
                    cur.execute("insert into %s values %s" % (table['name'], val))

            # Test query
            cur.execute(query)
            result = cur.fetchall()

        # prepare for next
        conn.rollback()

    return result
