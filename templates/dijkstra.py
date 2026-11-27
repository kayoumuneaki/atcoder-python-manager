# Dijkstra 法: 非負の重み付きグラフの最短距離
import heapq

INF = float("inf")


def dijkstra(graph, start):
    """graph[v] = [(to, cost), ...]。到達できない頂点の距離は INF。"""
    dist = [INF] * len(graph)
    dist[start] = 0
    heap = [(0, start)]

    while heap:
        d, v = heapq.heappop(heap)
        if d > dist[v]:
            continue

        for nv, cost in graph[v]:
            nd = d + cost
            if nd < dist[nv]:
                dist[nv] = nd
                heapq.heappush(heap, (nd, nv))

    return dist


# 使用例: N 頂点 M 辺の有向グラフ（頂点は 1-indexed で入力）
# n, m = map(int, input().split())
# graph = [[] for _ in range(n)]
# for _ in range(m):
#     a, b, c = map(int, input().split())
#     graph[a - 1].append((b - 1, c))
# print(dijkstra(graph, 0))
