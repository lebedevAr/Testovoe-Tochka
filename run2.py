import sys
from collections import defaultdict, deque


def get_graph(edges):
    graph = defaultdict(set)
    gates = set()

    for u, v in edges:
        graph[u].add(v)
        graph[v].add(u)

        # Определяем шлюзы
        if u.isupper():
            gates.add(u)
        if v.isupper():
            gates.add(v)

    return graph, gates


def find_shortest_path_to_gate(graph, gates, start):
    queue = deque([(start, [])])
    visited = set(start)

    while queue:
        current, path = queue.popleft()
        if current in gates:
            return path + [current]

        for neighbor in sorted(graph[current]):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [current]))

    return None


def get_next_move(graph, gates, cur_pos):
    # Находим все шлюзы и расстояния до них
    gates_dist = []
    for gateway in sorted(gates):
        queue = deque([(cur_pos, 0)])
        visited = set(cur_pos)
        is_found = False

        while queue and not is_found:
            node, dist = queue.popleft()

            if node == gateway:
                gates_dist.append((dist, gateway))
                break

            for neighbor in graph[node]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, dist + 1))

    if not gates_dist:
        return None

    # Выбираем ближайший шлюз
    min_dist = min(dist for dist, _ in gates_dist)
    target_gateways = (gw for dist, gw in gates_dist if dist == min_dist)
    target_gateway = min(target_gateways)

    # Находим следующий шаг к целевому шлюзу
    queue = deque([(cur_pos, [])])
    visited = set(cur_pos)

    while queue:
        current, path = queue.popleft()
        if current == target_gateway:
            if len(path) >= 1:
                return path[0]

        for neighbor in sorted(graph[current]):
            if neighbor not in visited:
                visited.add(neighbor)
                new_path = path + [current] if current != cur_pos else [neighbor]
                queue.append((neighbor, new_path))

    return None


def get_danger_gates(graph, gateways, virus_pos):
    dangered_gates = []
    for gateway in sorted(gateways):
        if virus_pos in graph[gateway]:
            dangered_gates.append(gateway)
    return dangered_gates


def find_gate_to_close_con(graph, gates, virus_pos):
    path = find_shortest_path_to_gate(graph, gates, virus_pos)
    if not path:
        return None

    # Находим первый шлюз на пути
    gate_on_path = None
    for node in path:
        if node in gates:
            gate_on_path = node
            break

    if not gate_on_path:
        return None

    # Находим узел, соединенный с этим шлюзом на пути вируса
    gate_neighbors = graph[gate_on_path]
    edges_to_cut = []
    for neighbor in gate_neighbors:
        if neighbor in path:
            edges_to_cut.append(f"{gate_on_path}-{neighbor}")

    if edges_to_cut:
        return min(edges_to_cut)


def solve(edges: list[tuple[str, str]]) -> list[str]:
    """
    Решение задачи об изоляции вируса

    Args:
        edges: список коридоров в формате (узел1, узел2)

    Returns:
        список отключаемых коридоров в формате "Шлюз-узел"
    """
    # Строим граф и определяем шлюзы
    graph, gateways = get_graph(edges)

    virus_pos = 'a'
    result = []

    while True:
        # 1. Проверяем шлюзы до которых вирус может дойти за 1 ход
        dangered_gates = get_danger_gates(graph, gateways, virus_pos)

        if dangered_gates:
            gate_to_close = min(dangered_gates)
            edge_to_cut = f"{gate_to_close}-{virus_pos}"
            result.append(edge_to_cut)
            gateway, node = edge_to_cut.split('-')
            graph[gateway].discard(node)
            graph[node].discard(gateway)

            virus_next_move = get_next_move(graph, gateways, virus_pos)
            if virus_next_move is None:
                break
            else:
                virus_pos = virus_next_move
        else:
            virus_next_move = get_next_move(graph, gateways, virus_pos)
            if virus_next_move is None:
                break

            # Находим оптимальное соединение для отключения на пути вируса
            edge_to_cut = find_gate_to_close_con(graph, gateways, virus_pos)
            if edge_to_cut:
                result.append(edge_to_cut)
                gateway, node = edge_to_cut.split('-')
                graph[gateway].discard(node)
                graph[node].discard(gateway)

            virus_pos = virus_next_move

    return result


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