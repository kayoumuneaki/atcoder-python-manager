# Fenwick Tree（BIT）: 一点加算・区間和
class FenwickTree:
    def __init__(self, n):
        self.n = n
        self.tree = [0] * (n + 1)

    def add(self, i, x):
        """i 番目（0-indexed）に x を加える。"""
        i += 1
        while i <= self.n:
            self.tree[i] += x
            i += i & -i

    def prefix_sum(self, r):
        """半開区間 [0, r) の和を返す。"""
        total = 0
        while r > 0:
            total += self.tree[r]
            r -= r & -r
        return total

    def sum(self, left, right):
        """半開区間 [left, right) の和を返す。"""
        return self.prefix_sum(right) - self.prefix_sum(left)


# 使用例
# ft = FenwickTree(5)
# for i, a in enumerate([1, 2, 3, 4, 5]):
#     ft.add(i, a)
# print(ft.sum(1, 4))  # 9
