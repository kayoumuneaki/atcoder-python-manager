# Union-Find（素集合データ構造）
class UnionFind:
    def __init__(self, n):
        # parent[x] < 0 なら x は根で、-parent[x] が集合の大きさ
        self.parent = [-1] * n

    def find(self, x):
        root = x
        while self.parent[root] >= 0:
            root = self.parent[root]

        # 経路圧縮
        while self.parent[x] >= 0:
            next_x = self.parent[x]
            self.parent[x] = root
            x = next_x

        return root

    def union(self, x, y):
        x = self.find(x)
        y = self.find(y)
        if x == y:
            return False

        # 大きい集合に小さい集合をつなぐ
        if self.parent[x] > self.parent[y]:
            x, y = y, x
        self.parent[x] += self.parent[y]
        self.parent[y] = x
        return True

    def same(self, x, y):
        return self.find(x) == self.find(y)

    def size(self, x):
        return -self.parent[self.find(x)]

    def group_count(self):
        return sum(1 for p in self.parent if p < 0)


# 使用例
# uf = UnionFind(5)
# uf.union(0, 1)
# print(uf.same(0, 1), uf.size(0))  # True 2
