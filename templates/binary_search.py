# 二分探索
from bisect import bisect_left, bisect_right


def binary_search(ok, ng, is_ok):
    """is_ok(ok) が True、is_ok(ng) が False となる境界を探す。
    返り値は is_ok が True になる ok 側の端。ok < ng でも ok > ng でもよい。"""
    while abs(ok - ng) > 1:
        mid = (ok + ng) // 2
        if is_ok(mid):
            ok = mid
        else:
            ng = mid
    return ok


def count_less(sorted_list, x):
    """ソート済みリストで x 未満の要素数。"""
    return bisect_left(sorted_list, x)


def count_less_equal(sorted_list, x):
    """ソート済みリストで x 以下の要素数。"""
    return bisect_right(sorted_list, x)


# 使用例: x * x <= 10 を満たす最大の x
# print(binary_search(0, 10**9, lambda x: x * x <= 10))  # 3
# print(count_less([1, 3, 3, 5], 3))  # 1
