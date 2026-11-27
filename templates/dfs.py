# DFS（深さ優先探索）: 再帰を使わないスタック版
def dfs(graph, start):
    """start から到達できる頂点を訪問順に返す。"""
    visited = [False] * len(graph)
    order = []
    stack = [start]

    while stack:
        v = stack.pop()
        if visited[v]:
            continue
        visited[v] = True
        order.append(v)

        # 番号の小さい頂点から訪問するため逆順に積む
        for nv in reversed(graph[v]):
            if not visited[nv]:
                stack.append(nv)

    return order


# 使用例
# graph = [[1, 2], [0, 3], [0], [1]]
# print(dfs(graph, 0))  # [0, 1, 3, 2]
