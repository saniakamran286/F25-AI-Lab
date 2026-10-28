import math

leaf_count = 0

def minimax(curDepth, nodeIndex, maxTurn, scores, targetDepth):
    global leaf_count
    if curDepth == targetDepth:
        leaf_count += 1
        return scores[nodeIndex]
    if maxTurn:
        return max(minimax(curDepth + 1, nodeIndex * 2, False, scores, targetDepth),
                   minimax(curDepth + 1, nodeIndex * 2 + 1, False, scores, targetDepth))
    else:
        return min(minimax(curDepth + 1, nodeIndex * 2, True, scores, targetDepth),
                   minimax(curDepth + 1, nodeIndex * 2 + 1, True, scores, targetDepth))

def alphabeta(depth, index, maxTurn, scores, target, alpha, beta):
    global leaf_count
    if depth == target:
        leaf_count += 1
        return scores[index]
    if maxTurn:
        value = float('-inf')
        for i in range(2):
            value = max(value, alphabeta(depth + 1, index * 2 + i, False, scores, target, alpha, beta))
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return value
    else:
        value = float('inf')
        for i in range(2):
            value = min(value, alphabeta(depth + 1, index * 2 + i, True, scores, target, alpha, beta))
            beta = min(beta, value)
            if alpha >= beta:
                break
        return value

def run_minimax(scores):
    global leaf_count
    leaf_count = 0
    s = list(scores)
    d = math.ceil(math.log2(len(s)))
    s += [0] * (2 ** d - len(s))
    return minimax(0, 0, True, s, d), leaf_count

def run_alphabeta(scores):
    global leaf_count
    leaf_count = 0
    d = int(math.log2(len(scores)))
    return alphabeta(0, 0, True, scores, d, float('-inf'), float('inf')), leaf_count

def order_line(name, scores):
    v, c = run_alphabeta(scores)
    print(f"{name + ':':<12}{scores} -> value {v}, leaves {c}")

if __name__ == "__main__":
    # Task 1 + 2: counter on both algorithms
    print("Minimax tree [3,5,2,9,0,7] (padded to 8 leaves)")
    v, c = run_minimax([3, 5, 2, 9, 0, 7])
    print(f"Minimax    -> value {v}, leaves {c}")
    t = [3, 5, 2, 9, 3, 5, 2, 9]
    print("Tree:", t)
    v, c = run_minimax(t)
    print(f"Minimax    -> value {v}, leaves {c}")
    v, c = run_alphabeta(t)
    print(f"Alpha-Beta -> value {v}, leaves {c}")
    print("-----")
    # Task 3: reorder branches
    order_line("Original", t)
    order_line("Best-case", [3, 5, 9, 2, 3, 5, 2, 9])
    order_line("Worst-case", [9, 2, 5, 3, 9, 2, 5, 3])
