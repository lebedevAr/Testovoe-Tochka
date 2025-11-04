import sys
from collections import defaultdict, deque
from typing import List, Tuple, Set, Optional


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
    gate_distances = []

    for gate in sorted(gates):
        queue = deque([(cur_pos, 0)])
        visited = set(cur_pos)

        while queue:
            node, dist = queue.popleft()

            if node == gate:
                gate_distances.append((dist, gate))
                break

            for neighbor in sorted(graph[node]):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, dist + 1))

    if not gate_distances:
        return None

    # Выбираем ближайший шлюз
    min_dist = min(dist for dist, _ in gate_distances)
    candidates = [gw for dist, gw in gate_distances if dist == min_dist]
    target_gate = min(candidates)

    # Находим следующий шаг к целевому шлюзу
    queue = deque([(cur_pos, [])])
    visited = set(cur_pos)

    while queue:
        current, path = queue.popleft()

        if current == target_gate:
            if path:
                return path[0]
            return None

        for neighbor in sorted(graph[current]):
            if neighbor not in visited:
                visited.add(neighbor)

                if current == cur_pos:
                    new_path = [neighbor]
                else:
                    new_path = path + [current]
                queue.append((neighbor, new_path))

    return None


def get_danger_gates(graph, gateways, virus_pos):
    dangered_gates = []
    for gateway in sorted(gateways):
        if virus_pos in graph[gateway]:
            dangered_gates.append(gateway)
    return dangered_gates


def find_optimal_blocking_sequence(start_node, blocked_edges, exit_edges, graph, gates):
    blocked_set = set(blocked_edges)

    # Пробуем каждое доступное ребро для блокировки
    for edge in exit_edges:
        if edge in blocked_set:
            continue

        new_blocked = blocked_edges + [edge]

        if len(new_blocked) == len(exit_edges):
            return True, new_blocked

        next_pos = get_next_move(graph, gates, start_node)
        if next_pos is None:
            return True, new_blocked

        if next_pos in gates:
            continue

        success, result = find_optimal_blocking_sequence(
            next_pos, new_blocked, exit_edges, graph, gates
        )

        if success:
            return True, result

    return False, None


def get_exit_edges(graph, gates):
    exit_edges = []
    for gate in sorted(gates):
        for neighbor in sorted(graph[gate]):
            if not neighbor.isupper():
                exit_edges.append((gate, neighbor))
    return exit_edges


def solve(edges: List[Tuple[str, str]]) -> List[str]:
    """
    Решение задачи об изоляции вируса

    Args:
        edges: список коридоров в формате (узел1, узел2)

    Returns:
        список отключаемых коридоров в формате "Шлюз-узел"
    """
    # Строим граф и определяем шлюзы
    graph, gates = get_graph(edges)

    # Получаем все соединения шлюзов с узлами
    exit_edges = get_exit_edges(graph, gates)

    is_success, result_edges = find_optimal_blocking_sequence("a", [], exit_edges, graph, gates)

    if not is_success or result_edges is None:
        return solve_old(edges)


    return [f"{gate}-{node}" for gate, node in result_edges]


def solve_old(edges: List[Tuple[str, str]]) -> List[str]:
    graph, gates = get_graph(edges)
    virus_pos = 'a'
    result = []

    while True:
        # Проверяем шлюзы, до которых вирус может дойти за 1 ход
        dangered_gates = get_danger_gates(graph, gates, virus_pos)

        if dangered_gates:
            gate_to_block = min(dangered_gates)
            edge_to_cut = f"{gate_to_block}-{virus_pos}"
            result.append(edge_to_cut)
            gate, node = edge_to_cut.split('-')
            graph[gate].discard(node)
            graph[node].discard(gate)

            # Проверяем, может ли вирус двигаться дальше
            next_move = get_next_move(graph, gates, virus_pos)
            if next_move is None:
                break
            else:
                virus_pos = next_move
        else:
            next_move = get_next_move(graph, gates, virus_pos)
            if next_move is None:
                break

            path = find_shortest_path_to_gate(graph, gates, virus_pos)
            if not path:
                break

            # Находим первый шлюз на пути и блокируем соединение с ним
            gate_on_path = None
            for node in path:
                if node in gates:
                    gate_on_path = node
                    break

            if gate_on_path:
                # Находим все соединения этого шлюза на пути вируса
                connections = []
                for neighbor in graph[gate_on_path]:
                    if neighbor in path:
                        connections.append(f"{gate_on_path}-{neighbor}")

                if connections:
                    edge_to_cut = min(connections)
                    result.append(edge_to_cut)
                    gate, node = edge_to_cut.split('-')
                    graph[gate].discard(node)
                    graph[node].discard(gate)

            virus_pos = next_move

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