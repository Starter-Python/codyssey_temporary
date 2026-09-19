"""Legend | 절차 생성 던전과 시야 계산."""

from __future__ import annotations

import random
from dataclasses import dataclass, field


WALL = 0
FLOOR = 1

MAP_WIDTH = 60
MAP_HEIGHT = 30
VIEW_RADIUS = 8


@dataclass
class Room:
    """던전 안의 네모 방."""

    x: int
    y: int
    w: int
    h: int

    @property
    def center(self) -> tuple[int, int]:
        return (self.x + self.w // 2, self.y + self.h // 2)

    def intersects(self, other: Room, pad: int = 1) -> bool:
        """여유(pad)를 두고 겹치는지 판정한다."""

        return (
            self.x - pad < other.x + other.w
            and self.x + self.w + pad > other.x
            and self.y - pad < other.y + other.h
            and self.y + self.h + pad > other.y
        )


@dataclass
class Dungeon:
    """한 층의 타일·방·계단 위치."""

    width: int
    height: int
    tiles: list[list[int]]
    rooms: list[Room] = field(default_factory=list)
    stairs: tuple[int, int] | None = None

    def walkable(self, x: int, y: int) -> bool:
        """밟을 수 있는 바닥인지 판정한다."""

        return 0 <= x < self.width and 0 <= y < self.height and self.tiles[y][x] == FLOOR

    def floor_tiles(self) -> list[tuple[int, int]]:
        """바닥 타일 전체 좌표를 반환한다."""

        return [
            (x, y)
            for y in range(self.height)
            for x in range(self.width)
            if self.tiles[y][x] == FLOOR
        ]


def _carve_h(tiles: list[list[int]], x1: int, x2: int, y: int) -> None:
    """가로 복도를 파낸다."""

    for x in range(min(x1, x2), max(x1, x2) + 1):
        if 0 <= x < len(tiles[0]) and 0 <= y < len(tiles):
            tiles[y][x] = FLOOR


def _carve_v(tiles: list[list[int]], y1: int, y2: int, x: int) -> None:
    """세로 복도를 파낸다."""

    for y in range(min(y1, y2), max(y1, y2) + 1):
        if 0 <= x < len(tiles[0]) and 0 <= y < len(tiles):
            tiles[y][x] = FLOOR


def gen_dungeon(seed: int, room_target: int = 8) -> Dungeon:
    """시드로 던전 1층을 생성한다. 같은 시드는 같은 지형을 만든다."""

    rng = random.Random(seed)
    tiles = [[WALL] * MAP_WIDTH for _ in range(MAP_HEIGHT)]
    rooms: list[Room] = []

    for _ in range(60):
        if len(rooms) >= room_target:
            break
        w, h = rng.randint(4, 10), rng.randint(3, 7)
        x, y = rng.randint(1, MAP_WIDTH - w - 1), rng.randint(1, MAP_HEIGHT - h - 1)
        candidate = Room(x, y, w, h)
        if any(candidate.intersects(other) for other in rooms):
            continue
        rooms.append(candidate)
        for ry in range(y, y + h):
            for rx in range(x, x + w):
                tiles[ry][rx] = FLOOR

    if not rooms:
        rooms.append(Room(2, 2, 8, 5))
        for ry in range(2, 7):
            for rx in range(2, 10):
                tiles[ry][rx] = FLOOR

    for prev, nxt in zip(rooms, rooms[1:]):
        x1, y1 = prev.center
        x2, y2 = nxt.center
        if rng.random() < 0.5:
            _carve_h(tiles, x1, x2, y1)
            _carve_v(tiles, y1, y2, x2)
        else:
            _carve_v(tiles, y1, y2, x1)
            _carve_h(tiles, x1, x2, y2)

    dungeon = Dungeon(MAP_WIDTH, MAP_HEIGHT, tiles, rooms, stairs=rooms[-1].center)
    return dungeon


def reachable_floors(dungeon: Dungeon) -> set[tuple[int, int]]:
    """시작 방에서 걸어서 닿는 바닥 전체를 반환한다 (연결 검증용)."""

    start = dungeon.rooms[0].center
    seen = {start}
    stack = [start]
    while stack:
        x, y = stack.pop()
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if dungeon.walkable(nx, ny) and (nx, ny) not in seen:
                seen.add((nx, ny))
                stack.append((nx, ny))
    return seen


def bresenham(x1: int, y1: int, x2: int, y2: int) -> list[tuple[int, int]]:
    """두 점 사이 격자 직선을 반환한다."""

    points = []
    dx, dy = abs(x2 - x1), abs(y2 - y1)
    sx, sy = (1 if x2 > x1 else -1), (1 if y2 > y1 else -1)
    err = dx - dy
    x, y = x1, y1
    while True:
        points.append((x, y))
        if (x, y) == (x2, y2):
            return points
        e2 = err * 2
        if e2 > -dy:
            err -= dy
            x += sx
        if e2 < dx:
            err += dx
            y += sy


def compute_fov(dungeon: Dungeon, px: int, py: int, radius: int = VIEW_RADIUS) -> set[tuple[int, int]]:
    """플레이어 기준 시야 집합을 반환한다. 벽 뒤는 가려진다."""

    visible = {(px, py)}
    for dy in range(-radius, radius + 1):
        for dx in range(-radius, radius + 1):
            if dx * dx + dy * dy > radius * radius:
                continue
            tx, ty = px + dx, py + dy
            if not (0 <= tx < dungeon.width and 0 <= ty < dungeon.height):
                continue
            for lx, ly in bresenham(px, py, tx, ty):
                visible.add((lx, ly))
                if (lx, ly) != (px, py) and dungeon.tiles[ly][lx] == WALL:
                    break
    return visible
