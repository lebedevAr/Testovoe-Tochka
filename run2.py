import sys
from collections import defaultdict, deque
from typing import List, Tuple, Set, Optional


def get_graph(edges):
    graph = defaultdict(set)
    for u, v in edges:
        graph[u].add(v)
        graph[v].add(u)
    return dict(graph)


def get_virus_move(graph, virus_pos):
    nodes = set(graph.keys())
    gates = sorted([n for n in nodes if n and n.isupper()])

    target_gate = None
    best_dist = float('inf')
    dist_map = None

    for gate in gates:
        dist = {gate: 0}
        queue = deque([gate])

        while queue:
            cur = queue.popleft()
            for neighbor in graph.get(cur, set()):
                if neighbor not in dist:
                    dist[neighbor] = dist[cur] + 1
                    queue.append(neighbor)

        if virus_pos not in dist:
            continue

        distance = dist[virus_pos]
        if distance == best_dist and gate < target_gate or distance < best_dist:
            target_gate = gate
            best_dist = distance
            dist_map = dist

    if target_gate is None:
        return None

    # Если вирус уже у шлюза
    if best_dist == 0:
        return target_gate, target_gate, dist_map

    # Находим следующий шаг к целевому шлюзу
    candidates = []
    for neighbor in sorted(graph.get(virus_pos, [])):
        if dist_map.get(neighbor, float('inf')) == best_dist - 1:
            candidates.append(neighbor)

    if not candidates:
        return None

    next_node = candidates[0]
    return target_gate, next_node, dist_map


def search_solution(edges, virus_pos):
    graph = get_graph(set(edges))
    move = get_virus_move(graph, virus_pos)

    # Если вирус не может достичь ни одного шлюза - решение найдено
    if move is None:
        return None, []

    # Собираем все возможные отключения
    candidates = []
    for edge in edges:
        u, v = edge
        if u.isupper() and not v.isupper():
            candidates.append((u, v))
        elif v.isupper() and not u.isupper():
            candidates.append((v, u))
    unique_candidates = sorted(set(candidates))

    for gate, node in unique_candidates:
        if gate <= node:
            edge_canonical = (gate, node)
        else:
            edge_canonical = (node, gate)
        if edge_canonical not in edges:
            continue

        new_edges = set(edges) - {edge_canonical}
        new_edges_frozen = frozenset(new_edges)

        # Проверяем, может ли вирус двигаться после отключения
        new_graph = get_graph(new_edges)
        new_move = get_virus_move(new_graph, virus_pos)
        if new_move is None:
            return (gate, node), []

        _, next_pos, _ = new_move

        # Если вирус сразу попал в шлюз - этот вариант не подходит
        if next_pos.isupper():
            continue

        result = search_solution(new_edges_frozen, next_pos)
        if result:
            first_edge, rest_edges = result
            solution = [(gate, node)]
            if first_edge:
                solution.append(first_edge)
            solution.extend(rest_edges)
            if solution:
                return solution[0], solution[1:]
            else:
                return None, []
    return None


def solve(edges: List[Tuple[str, str]]) -> List[str]:
    """
        Решение задачи об изоляции вируса

        Args:
            edges: список коридоров в формате (узел1, узел2)

        Returns:
            список отключаемых коридоров в формате "Шлюз-узел"
    """
    # Преобразуем рёбра в каноническую форму
    canonical_edges = {(u, v) if u <= v else (v, u) for u, v in edges}
    edges_frozen = frozenset(canonical_edges)

    sequence = []
    current_edges = edges_frozen
    current_virus = 'a'

    while True:
        # Ищем следующее отключение
        result = search_solution(current_edges, current_virus)
        if result is None:
            break

        first_edge, _ = result
        if first_edge is None:
            break

        sequence.append(first_edge)

        if first_edge[0] <= first_edge[1]:
            edge_to_remove = (first_edge[0], first_edge[1])
        else:
            edge_to_remove = (first_edge[1], first_edge[0])
        current_edges = current_edges - {edge_to_remove}

        # Симулируем ход вируса
        current_graph = get_graph(current_edges)
        move = get_virus_move(current_graph, current_virus)

        if move is None:
            break

        _, next_pos, _ = move
        if next_pos.isupper():
            break

        current_virus = next_pos

    return [f"{gate}-{node}" for gate, node in sequence]


def main():
    edges = []
    for line in sys.stdin:
        line = line.strip()
        if line:
            node1, sep, node2 = line.partition('-')
            if sep:
                edges.append((node1, node2))

    result = solve(edges)
    for edge in result:
        print(edge)


if __name__ == "__main__":
    main()