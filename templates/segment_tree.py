# セグメント木: 一点更新・区間取得（op は結合法則を満たす演算）
class SegmentTree:
    def __init__(self, values, op, identity):
        """values: 初期配列, op: 演算, identity: 単位元（例: min なら INF）"""
        self.n = len(values)
        self.op = op
        self.identity = identity
        self.size = 1
        while self.size < self.n:
            self.size *= 2

        self.tree = [identity] * (2 * self.size)
        for i, value in enumerate(values):
            self.tree[self.size + i] = value
        for i in range(self.size - 1, 0, -1):
            self.tree[i] = op(self.tree[2 * i], self.tree[2 * i + 1])

    def update(self, i, value):
        """i 番目（0-indexed）を value に変更する。"""
        i += self.size
        self.tree[i] = value
        i //= 2
        while i:
            self.tree[i] = self.op(self.tree[2 * i], self.tree[2 * i + 1])
            i //= 2

    def get(self, i):
        return self.tree[self.size + i]

    def query(self, left, right):
        """半開区間 [left, right) の演算結果を返す。"""
        left_result = self.identity
        right_result = self.identity
        left += self.size
        right += self.size

        while left < right:
            if left & 1:
                left_result = self.op(left_result, self.tree[left])
                left += 1
            if right & 1:
                right -= 1
                right_result = self.op(self.tree[right], right_result)
            left //= 2
            right //= 2

        return self.op(left_result, right_result)


# 使用例: 区間最小値
# st = SegmentTree([5, 3, 8, 1], min, float("inf"))
# print(st.query(0, 3))  # 3
# st.update(1, 10)
# print(st.query(0, 3))  # 5
