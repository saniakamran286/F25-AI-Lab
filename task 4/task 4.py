import heapq

def astar(graph, h, start, goal):
    pq = [(h[start], 0, start, 0, [start])]
    best = {start: 0}
    n = expanded = 0
    while pq:
        f, _, node, g, path = heapq.heappop(pq)
        if g != best[node]:
            continue
        if node == goal:
            return g, path, expanded
        expanded += 1
        for nxt, w in graph.get(node, []):
            ng = g + w
            if ng < best.get(nxt, float("inf")):
                best[nxt] = ng
                n += 1
                heapq.heappush(pq, (ng + h[nxt], n, nxt, ng, path + [nxt]))

g = {"S": [("A", 1), ("B", 4)], "A": [("C", 2)], "B": [("G", 5)], "C": [("G", 3)], "G": []}
h = {"S": 5, "A": 4, "B": 4, "C": 2, "G": 0}

print(astar(g, h, "S", "G"))
print(astar(g, {k: 0 for k in h}, "S", "G"))
h["C"] = 10
print(astar(g, h, "S", "G"))
