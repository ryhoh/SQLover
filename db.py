import sqlite3
from typing import List, Tuple, Any, Union


def execute(
        ddl: Union[str, List[str]],
        query: str
) -> List[Tuple[Any, ...]]:
    """
    独立した sqlite3 データベース上で，テーブル作成とクエリを実行する

    :param ddl: テーブル作成に用いる DDL
    :param query: 実行するクエリ
    :return: クエリ結果
    """

    with sqlite3.connect(":memory:") as conn:  # メモリ上に作成すると，close 時に解放される
        cur = conn.cursor()
        if isinstance(ddl, str):
            cur.execute(ddl)
        else:
            for line in ddl:
                cur.execute(line)
        cur.execute(query)
        result = cur.fetchall()
        cur.close()
        return result
