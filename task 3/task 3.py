# Lab 3: BFS, DFS, DLS, IDDFS and UCS

G = {
    'A': ['B', 'C'],
    'B': ['D', 'E'],
    'C': ['F'],
    'D': ['E'],
    'E': ['G'],
    'F': ['G'],
    'G': []
}


def bfs(start, goal):
    queue = [[start]]
    visited = []

    while queue:
        path = queue.pop(0)
        node = path[-1]
        if node == goal:
            return path
        if node not in visited:
            visited.append(node)
            for child in G[node]:
                queue.append(path + [child])


def dfs(start, goal):
    stack = [[start]]
    visited = []

    while stack:
        path = stack.pop()
        node = path[-1]
        if node == goal:
            return path
        if node not in visited:
            visited.append(node)
            for child in G[node]:
                stack.append(path + [child])


def dls(node, goal, limit, path):
    if node == goal:
        return path
    if limit == 0:
        return None

    for child in G[node]:
        answer = dls(child, goal, limit - 1, path + [child])
        if answer:
            return answer
    return None


# Weighted graph for UCS
W = {
    'A': [('B', 5), ('C', 1)],
    'B': [('D', 1), ('E', 10)],
    'C': [('F', 1), ('E', 2)],
    'D': [('E', 1)],
    'E': [('G', 1)],
    'F': [('G', 1)],
    'G': []
}


def ucs(start, goal):
    queue = [(0, [start])]

    while queue:
        queue.sort()
        cost, path = queue.pop(0)
        node = path[-1]

        if node == goal:
            return path, cost

        for child, weight in W[node]:
            queue.append((cost + weight, path + [child]))


def show(path):
    if path:
        return ' -> '.join(path)
    return 'Not found'


print('BFS:', show(bfs('A', 'G')))
print('DFS:', show(dfs('A', 'G')))

for limit in range(1, 5):
    path = dls('A', 'G', limit, ['A'])
    print('DLS limit', limit, ':', show(path))

for limit in range(5):
    path = dls('A', 'G', limit, ['A'])
    print('IDDFS limit', limit, ':', show(path))
    if path:
        break

path, cost = ucs('A', 'G')
print('UCS:', show(path), 'Cost:', cost)
