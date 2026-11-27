# BFS（幅優先探索）: 重みなしグラフの最短距離
from collections import deque


def bfs(graph, start):
    """graph: 隣接リスト。到達できない頂点の距離は -1。"""
    dist = [-1] * len(graph)
    dist[start] = 0
    queue = deque([start])

    while queue:
        v = queue.popleft()
        for nv in graph[v]:
            if dist[nv] == -1:
                dist[nv] = dist[v] + 1
                queue.append(nv)

    return dist


# 使用例: N 頂点 M 辺の無向グラフ（頂点は 1-indexed で入力）
# n, m = map(int, input().split())
# graph = [[] for _ in range(n)]
# for _ in range(m):
#     u, v = map(int, input().split())
#     graph[u - 1].append(v - 1)
#     graph[v - 1].append(u - 1)
# print(bfs(graph, 0))
