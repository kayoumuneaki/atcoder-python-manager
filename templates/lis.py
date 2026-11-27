# LIS（最長増加部分列）の長さ: O(N log N)
from bisect import bisect_left, bisect_right


def lis_length(values, strict=True):
    """strict=True なら狭義単調増加、False なら広義単調増加（同じ値を許す）。"""
    tails = []
    for x in values:
        if strict:
            i = bisect_left(tails, x)
        else:
            i = bisect_right(tails, x)

        if i == len(tails):
            tails.append(x)
        else:
            tails[i] = x

    return len(tails)


# 使用例
# print(lis_length([3, 1, 4, 1, 5, 9, 2, 6]))  # 4
