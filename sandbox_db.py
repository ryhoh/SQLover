import sqlite3
from typing import List, Dict, Tuple, Any, Union


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

    with sqlite3.connect(":memory:") as conn:  # メモリ上に作成すると，close 時に解放される
        cur = conn.cursor()

        # Make tables
        if isinstance(ddl, str):
            cur.execute(ddl)
        elif '__iter__' in dir(ddl):
            for line in ddl:
                cur.execute(line)
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
        cur.close()
        return result
