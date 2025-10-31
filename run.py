import sys
import heapq

#test
ROOM_INFO = {"room_depth": 0, "entrances": [2, 4, 6, 8]}
ENERGY_COST = {'A': 1, 'B': 10, 'C': 100, 'D': 1000}
TARGETS = {'A': 0, 'B': 1, 'C': 2, 'D': 3}


def parse_input(lines):
    rooms = [[] for _ in range(4)]

    if ROOM_INFO["room_depth"] == 2:
        for i in range(4):
            rooms[i].append(lines[2][3 + i * 2])
            rooms[i].append(lines[3][3 + i * 2])
    else:
        for i in range(4):
            rooms[i].append(lines[2][3 + i * 2])
            rooms[i].append(lines[3][3 + i * 2])
            rooms[i].append(lines[4][3 + i * 2])
            rooms[i].append(lines[5][3 + i * 2])

    # Преобразуем в кортежи для хеширования
    rooms_tuple = tuple(tuple(room) for room in rooms)
    return rooms_tuple


def get_room_position(room):
    for i in range(ROOM_INFO["room_depth"] - 1, -1, -1):
        if room[i] == '.':
            return i
    return -1


def is_hallway_clear(hallway, start, end):
    step = 1 if start < end else -1
    for pos in range(start + step, end + step, step):
        if hallway[pos] != '.':
            return False
    return True


def get_moves_from_room(rooms, hallway, room_idx):
    moves = []
    room = rooms[room_idx]

    # Находим верхний объект в комнате
    top_idx = -1
    for i in range(ROOM_INFO["room_depth"]):
        if room[i] != '.':
            top_idx = i
            break

    if top_idx == -1:  # Комната пуста
        return moves

    char = room[top_idx]
    entrance = ROOM_INFO["entrances"][room_idx]

    # Если комната уже заполнена, то не выходим из нее
    if (all(c == char for c in room) and
            all(room[j] == char for j in range(top_idx, ROOM_INFO["room_depth"]))):
        return moves

    # Перемещаемся в разрешенные позиции коридора
    for hall_pos in [0, 1, 3, 5, 7, 9, 10]:
        if is_hallway_clear(hallway, entrance, hall_pos):
            steps = top_idx + 1 + abs(entrance - hall_pos)
            cost = steps * ENERGY_COST[char]
            moves.append((room_idx, top_idx, hall_pos, cost, char))

    return moves


def get_moves_to_room(rooms, hallway, hall_pos):
    moves = []
    char = hallway[hall_pos]
    target_room_idx = TARGETS[char]
    target_room = rooms[target_room_idx]
    entrance = ROOM_INFO["entrances"][target_room_idx]

    if not all(c in (char, '.') for c in target_room):
        return moves

    if not is_hallway_clear(hallway, hall_pos, entrance):
        return moves

    # Находим позицию для вставки в комнату
    room_pos = get_room_position(target_room)
    if room_pos == -1:
        return moves

    steps = abs(hall_pos - entrance) + room_pos + 1
    cost = steps * ENERGY_COST[char]
    moves.append((hall_pos, target_room_idx, room_pos, cost, char))

    return moves


def find_solution(initial_rooms):
    # Начальное состояние: пустой коридор
    initial_hallway = tuple('.' for _ in range(11))
    initial_state = (initial_hallway, initial_rooms)

    # Целевое состояние
    target_rooms = (
        tuple('A' for _ in range(ROOM_INFO["room_depth"])),
        tuple('B' for _ in range(ROOM_INFO["room_depth"])),
        tuple('C' for _ in range(ROOM_INFO["room_depth"])),
        tuple('D' for _ in range(ROOM_INFO["room_depth"]))
    )
    target_hallway = tuple('.' for _ in range(11))
    target_state = (target_hallway, target_rooms)

    # Алгоритм Дейкстры
    dist = {initial_state: 0}
    heap = [(0, initial_state)]

    while heap:
        current_cost, current_state = heapq.heappop(heap)
        hallway, rooms = current_state

        if current_state == target_state:
            return current_cost

        if current_cost > dist[current_state]:
            continue

        # Перемещения из комнат в коридор
        for room_idx in range(4):
            moves = get_moves_from_room(rooms, hallway, room_idx)
            for room_idx, room_pos, hall_pos, move_cost, char in moves:
                # Создаем новое состояние
                new_hallway = list(hallway)
                new_rooms = [list(room) for room in rooms]

                new_hallway[hall_pos] = char
                new_rooms[room_idx][room_pos] = '.'

                new_hallway = tuple(new_hallway)
                new_rooms = tuple(tuple(room) for room in new_rooms)
                new_state = (new_hallway, new_rooms)
                new_cost = current_cost + move_cost

                if new_state not in dist or new_cost < dist[new_state]:
                    dist[new_state] = new_cost
                    heapq.heappush(heap, (new_cost, new_state))

        # Перемещения из коридора в комнаты
        for hall_pos in range(11):
            if hallway[hall_pos] != '.':
                moves = get_moves_to_room(rooms, hallway, hall_pos)
                for hall_pos, room_idx, room_pos, move_cost, char in moves:
                    # Создаем новое состояние
                    new_hallway = list(hallway)
                    new_rooms = [list(room) for room in rooms]

                    new_hallway[hall_pos] = '.'
                    new_rooms[room_idx][room_pos] = char

                    new_hallway = tuple(new_hallway)
                    new_rooms = tuple(tuple(room) for room in new_rooms)

                    new_state = (new_hallway, new_rooms)
                    new_cost = current_cost + move_cost

                    if new_state not in dist or new_cost < dist[new_state]:
                        dist[new_state] = new_cost
                        heapq.heappush(heap, (new_cost, new_state))

    return -1


def solve(lines: list[str]) -> int:
    """
    Решение задачи о сортировке в лабиринте

    Args:
        lines: список строк, представляющих лабиринт

    Returns:
        минимальная энергия для достижения целевой конфигурации
    """

    if len(lines) == 5:
        ROOM_INFO["room_depth"] = 2
    else:
        ROOM_INFO["room_depth"] = 4

    initial_rooms = parse_input(lines)

    return find_solution(initial_rooms)


def main():
    # Чтение входных данных
    lines = []
    for line in sys.stdin:
        lines.append(line.rstrip('\n'))

    result = solve(lines)
    print(result)


if __name__ == "__main__":
    main()