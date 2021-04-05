from typing import List, Tuple, Any, Optional


def judge(
        expected: List[Tuple[Any, ...]],
        answered: List[Tuple[Any, ...]],
        order_strict: bool
) -> Tuple[bool, Optional[int]]:
    """
    クエリ結果が模範解答と等しいかを比べる

    :param expected: 模範解答
    :param answered: 提出解答
    :param order_strict: ORDER BY などで順序一致を求めるか
    :return: (正解したか, 不正解の場合 answered の最初の不適切行)
    """

    if order_strict:  # 順序まで要求する場合
        correct = expected == answered
        if correct:
            return True, None
        for idx, (expected_record, answered_record) in enumerate(zip(expected, answered), start=1):
            if expected_record != answered_record:
                return False, idx  # 最初に不一致した行の番号を返す

    expected_set = set(expected)
    for idx, answered_record in enumerate(answered, start=1):  # answer を1行ずつチェック
        if answered_record in expected_set:
            expected_set.remove(answered_record)
        else:
            return False, idx  # 存在しないとき，その行の番号を返す

    if len(expected_set) != 0:  # answer にレコードの不足がある場合
        return False, len(expected_set) + 1

    return True, None
