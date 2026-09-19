"""Legend FPS | 터미널 레이캐스팅 FPS. 표준 라이브러리만 사용."""

from __future__ import annotations

import math
import random
import select
import sys
import termios
import time
import tty
from pathlib import Path

BASE_DIR = Path(__file__).parent
SCORES_FILE = BASE_DIR / "fps_scores.json"

SCREEN_W, SCREEN_H = 72, 22
FOV = math.radians(66)
MOVE_SPEED = 2.6
TURN_SPEED = 2.4
STEP_MOVE = 0.16
STEP_STRAFE = 0.13
STEP_TURN = 0.11
FPS = 20
SHOT_DAMAGE = 34
PLAYER_HP = 120
KILL_HEAL = 10
ENEMY_HP = 100
ENEMY_SPEED = 1.0
ENEMY_DAMAGE = 6
ENEMY_REACH = 0.6
FINAL_WAVE = 5

MAP = [
    "########################",
    "#P.....#.......#.......#",
    "#......#.......#...B...#",
    "#......#.......#.......#",
    "#......###.#####.####..#",
    "#..........#.....#.....#",
    "#......#...#..E..#..E..#",
    "####.###...#.....#.....#",
    "#......#...###.###.##..#",
    "#..E...#.....W.....#...#",
    "#......#...........#.E.#",
    "#..####.#####.######...#",
    "#..#......#......#..#..#",
    "#..#..E...#..E...#..#..#",
    "#..#......#......#.....#",
    "#..#####.######.#####..#",
    "#......................#",
    "########################",
]

WALL_COLORS = {"#": "37", "B": "31", "W": "33"}
SHADES = [(1.5, "█"), (3.0, "▓"), (5.0, "▒"), (8.0, "░"), (float("inf"), "·")]


def shade(dist: float) -> str:
    """거리에 맞는 음영 문자를 반환한다."""

    for limit, glyph in SHADES:
        if dist < limit:
            return glyph
    return "·"


def cast_ray(grid: list[str], px: float, py: float, rdx: float, rdy: float) -> tuple[float, int, str]:
    """DDA로 광선을 쏴 (보정거리, 면, 벽종류)를 반환한다."""

    map_x, map_y = int(px), int(py)
    delta_x = abs(1.0 / rdx) if rdx else float("inf")
    delta_y = abs(1.0 / rdy) if rdy else float("inf")
    if rdx < 0:
        step_x, side_x = -1, (px - map_x) * delta_x
    else:
        step_x, side_x = 1, (map_x + 1.0 - px) * delta_x
    if rdy < 0:
        step_y, side_y = -1, (py - map_y) * delta_y
    else:
        step_y, side_y = 1, (map_y + 1.0 - py) * delta_y
    height = len(grid)
    while True:
        if side_x < side_y:
            side_x += delta_x
            map_x += step_x
            side = 0
        else:
            side_y += delta_y
            map_y += step_y
            side = 1
        if not (0 <= map_y < height and 0 <= map_x < len(grid[map_y])):
            return float("inf"), side, "#"
        cell = grid[map_y][map_x]
        if cell != ".":
            dist = side_x - delta_x if side == 0 else side_y - delta_y
            return max(dist, 0.0001), side, cell


def parse_map(raw: list[str]) -> tuple[list[str], tuple[float, float], list[tuple[float, float]]]:
    """맵에서 플레이어 시작점과 적 스폰점을 꺼내고 지형을 정리한다."""

    grid, spawns = [], []
    start = (1.5, 1.5)
    for y, row in enumerate(raw):
        line = list(row)
        for x, ch in enumerate(line):
            if ch == "P":
                start = (x + 0.5, y + 0.5)
                line[x] = "."
            elif ch == "E":
                spawns.append((x + 0.5, y + 0.5))
                line[x] = "."
        grid.append("".join(line))
    width = max(len(row) for row in grid)
    grid = [row.ljust(width) for row in grid]
    return grid, start, spawns


class Enemy:
    """추적·근접 공격을 하는 적."""

    def __init__(self, x: float, y: float, hp: int = ENEMY_HP) -> None:
        self.x, self.y = x, y
        self.hp = hp
        self.cool = 0.0

    @property
    def alive(self) -> bool:
        return self.hp > 0


class Game:
    """FPS 한 판의 상태와 프레임을 관리한다."""

    def __init__(self, wave: int = 1, rng: random.Random | None = None) -> None:
        self.rng = rng or random.Random()
        self.grid, start, self.spawns = parse_map(MAP)
        self.px, self.py = start
        self.angle = 0.0
        self.hp = PLAYER_HP
        self.max_hp = PLAYER_HP
        self.wave = 0
        self.kills = 0
        self.score = 0
        self.enemies: list[Enemy] = []
        self.over = False
        self.won = False
        self.flash = 0.0
        self.next_wave()

    # -- 이동·회전 --------------------------------------------------------

    def solid(self, x: float, y: float) -> bool:
        cell = self.grid[int(y)][int(x)]
        return cell != "."

    def move(self, forward: float, strafe: float, dt: float) -> None:
        """충돌 슬라이딩 이동. forward/strafe는 -1~1."""

        dx = math.cos(self.angle) * forward + math.cos(self.angle + math.pi / 2) * strafe
        dy = math.sin(self.angle) * forward + math.sin(self.angle + math.pi / 2) * strafe
        nx = self.px + dx * MOVE_SPEED * dt
        if not self.solid(nx, self.py):
            self.px = nx
        ny = self.py + dy * MOVE_SPEED * dt
        if not self.solid(self.px, ny):
            self.py = ny

    def turn(self, direction: float, dt: float) -> None:
        self.angle += direction * TURN_SPEED * dt

    def step(self, forward: int, strafe: int) -> None:
        """키 한 번에 고정 거리 이동. 프레임과 무관해 조작이 일정하다."""

        if forward:
            self.move(forward, 0, STEP_MOVE / MOVE_SPEED)
        if strafe:
            self.move(0, strafe, STEP_STRAFE / MOVE_SPEED)

    def turn_step(self, direction: int) -> None:
        """키 한 번에 고정 각도 회전."""

        self.angle += direction * STEP_TURN

    # -- 전투 -------------------------------------------------------------

    def shoot(self) -> str:
        """화면 중앙 히트스캔. 맞으면 데미지, 메시지를 반환한다."""

        self.flash = 0.12
        target = self._aim_target()
        if target is None:
            return "빗나갔다..."
        enemy, _ = target
        enemy.hp -= SHOT_DAMAGE
        if enemy.hp <= 0:
            self.kills += 1
            gained = 100 + self.wave * 20
            self.score += gained
            self.hp = min(self.max_hp, self.hp + KILL_HEAL)
            msg = f"처치! +{gained}점, 체력 +{KILL_HEAL}"
            if all(not e.alive for e in self.enemies):
                self._wave_cleared()
            return msg
        return f"명중! 적 체력 {max(enemy.hp, 0)}"

    def _aim_target(self) -> tuple[Enemy, float] | None:
        """중앙 조준선 위 가장 가까운 적을 반환한다."""

        best = None
        dir_x, dir_y = math.cos(self.angle), math.sin(self.angle)
        half_fov = FOV / 2
        for enemy in self.enemies:
            if not enemy.alive:
                continue
            rel_x, rel_y = enemy.x - self.px, enemy.y - self.py
            dist = math.hypot(rel_x, rel_y)
            if dist < 0.2:
                continue
            ang_diff = abs((math.atan2(rel_y, rel_x) - self.angle + math.pi) % (2 * math.pi) - math.pi)
            size_angle = min(0.35, 1.1 / max(dist, 0.5))
            if ang_diff > size_angle:
                continue
            wall_dist, _, _ = cast_ray(self.grid, self.px, self.py, dir_x, dir_y)
            if dist < wall_dist + 0.3 and (best is None or dist < best[1]):
                best = (enemy, dist)
        return best

    def aim_info(self) -> str:
        """조준 중인 적 정보를 반환한다. 없으면 빈 문자열."""

        target = self._aim_target()
        if target is None:
            return ""
        enemy, dist = target
        return f"🎯 조준중: 적 체력 {max(enemy.hp, 0)} (거리 {dist:.1f})"

    def _wave_cleared(self) -> None:
        if self.wave >= FINAL_WAVE:
            self.won = True
            self.over = True
            self.score += 1000
        else:
            self.next_wave()

    def next_wave(self) -> None:
        """다음 웨이브 적을 스폰한다."""

        self.wave += 1
        spots = list(self.spawns)
        self.rng.shuffle(spots)
        count = min(3 + self.wave, len(spots))
        for x, y in spots[:count]:
            hp = ENEMY_HP + (self.wave - 1) * 20
            self.enemies.append(Enemy(x, y, hp))

    def update_enemies(self, dt: float) -> None:
        """적 이동·공격을 한 프레임 진행한다."""

        for enemy in self.enemies:
            if not enemy.alive:
                continue
            enemy.cool = max(0.0, enemy.cool - dt)
            dx, dy = self.px - enemy.x, self.py - enemy.y
            dist = math.hypot(dx, dy)
            if dist <= ENEMY_REACH:
                if enemy.cool <= 0:
                    enemy.cool = 1.0
                    self.hp -= ENEMY_DAMAGE
                    if self.hp <= 0:
                        self.hp = 0
                        self.over = True
                        return
            elif dist < 12:
                step = ENEMY_SPEED * dt
                nx = enemy.x + dx / dist * step
                if not self.solid(nx, enemy.y):
                    enemy.x = nx
                ny = enemy.y + dy / dist * step
                if not self.solid(enemy.x, ny):
                    enemy.y = ny

    # -- 렌더링 ------------------------------------------------------------

    def render(self) -> tuple[str, list[float]]:
        """화면 문자열과 뎁스버퍼를 반환한다."""

        dir_x, dir_y = math.cos(self.angle), math.sin(self.angle)
        plane_x, plane_y = -dir_y * math.tan(FOV / 2), dir_x * math.tan(FOV / 2)
        zbuf: list[float] = []
        cols: list[list[str]] = [[" "] * SCREEN_H for _ in range(SCREEN_W)]
        for col in range(SCREEN_W):
            cam = 2 * col / SCREEN_W - 1
            rdx, rdy = dir_x + plane_x * cam, dir_y + plane_y * cam
            dist, side, wall = cast_ray(self.grid, self.px, self.py, rdx, rdy)
            zbuf.append(dist)
            height = min(SCREEN_H, int(SCREEN_H / dist))
            top = SCREEN_H // 2 - height // 2
            color = WALL_COLORS.get(wall, "37")
            dim = "\033[2m" if side == 1 else ""
            glyph = shade(dist)
            for y in range(top, top + height):
                cols[col][y] = f"\033[{dim}{color}m{glyph}\033[0m"
        self._draw_sprites(cols, zbuf, dir_x, dir_y, plane_x, plane_y)
        lines = ["".join(cols[c][r] for c in range(SCREEN_W)) for r in range(SCREEN_H)]
        mid = SCREEN_H // 2
        center = [cols[c][mid] for c in range(SCREEN_W)]
        center[SCREEN_W // 2 - 1] = "\033[1;33m+\033[0m"
        lines[mid] = "".join(center)
        panel = [line for line in self._panel()]
        while panel and panel[-1] == "":
            panel.pop()
        body = lines + ["-" * SCREEN_W] + panel
        status = "\033[1;33m*** 발사! ***\033[0m" if self.flash > 0 else ""
        return status + "\n" + "\n".join(body), zbuf

    def _draw_sprites(self, cols: list[list[str]], zbuf: list[float], dir_x: float, dir_y: float, plane_x: float, plane_y: float) -> None:
        """적 스프라이트를 거리순으로 그린다."""

        inv = 1.0 / (plane_x * dir_y - dir_x * plane_y)
        order = sorted(
            (e for e in self.enemies if e.alive),
            key=lambda e: (e.x - self.px) ** 2 + (e.y - self.py) ** 2,
            reverse=True,
        )
        for enemy in order:
            rel_x, rel_y = enemy.x - self.px, enemy.y - self.py
            trans_y = inv * (-plane_y * rel_x + plane_x * rel_y)
            if trans_y < 0.2:
                continue
            trans_x = inv * (dir_y * rel_x - dir_x * rel_y)
            screen_x = int(SCREEN_W / 2 * (1 + trans_x / trans_y))
            size = min(SCREEN_H, int(SCREEN_H / trans_y))
            top = SCREEN_H // 2 - size // 2
            for stripe in range(max(0, screen_x - size // 4), min(SCREEN_W, screen_x + size // 4 + 1)):
                if trans_y >= zbuf[stripe]:
                    continue
                for y in range(max(0, top), min(SCREEN_H, top + size)):
                    rel = (y - top) / max(size, 1)
                    if rel < 0.18:
                        cols[stripe][y] = "\033[1;33mO\033[0m"
                    else:
                        cols[stripe][y] = "\033[1;31m█\033[0m"

    def _panel(self) -> list[str]:
        """우측 상태 패널(HP·점수·미니맵)을 만든다."""

        hp_bar = "█" * (self.hp * 10 // self.max_hp) + "░" * (10 - self.hp * 10 // self.max_hp)
        lines = [
            f"WAVE {self.wave}/{FINAL_WAVE}",
            f"HP [\033[1;31m{hp_bar}\033[0m] {self.hp}",
            f"점수 {self.score}  처치 {self.kills}",
            "",
            "[미니맵]",
        ]
        gx, gy = int(self.px), int(self.py)
        for y in range(max(0, gy - 3), min(len(self.grid), gy + 4)):
            row = ""
            for x in range(max(0, gx - 5), min(len(self.grid[0]), gx + 6)):
                if (x, y) == (gx, gy):
                    row += "\033[1;33m@\033[0m"
                elif any(e.alive and int(e.x) == x and int(e.y) == y for e in self.enemies):
                    row += "\033[1;31mE\033[0m"
                else:
                    row += "#" if self.grid[y][x] != "." else "·"
            lines.append(row)
        lines += ["", "W/S이동 A/D옆걸음", "←/→회전 Space발사", "Q 종료"]
        while len(lines) < SCREEN_H + 1:
            lines.append("")
        return lines[: SCREEN_H + 1]

    # -- 저장 ---------------------------------------------------------------

    def save_score(self, name: str, path: Path = SCORES_FILE) -> list[dict]:
        import json

        try:
            with open(path, encoding="utf-8") as file:
                scores = json.load(file)
        except (FileNotFoundError, ValueError, OSError):
            scores = []
        scores.append({"name": name, "score": self.score, "wave": self.wave, "kills": self.kills, "won": self.won})
        scores.sort(key=lambda s: int(s.get("score", 0)), reverse=True)
        with open(path, "w", encoding="utf-8") as file:
            json.dump(scores[:10], file, ensure_ascii=False, indent=2)
        return scores[:10]


def read_keys() -> list[str]:
    """대기 중인 키를 모두 읽는다. 화살표 키도 해석한다."""

    keys = []
    while select.select([sys.stdin], [], [], 0)[0]:
        ch = sys.stdin.read(1)
        if ch == "\x1b":
            seq = ch + sys.stdin.read(2)
            keys.append({"[D": "left", "[C": "right"}.get(seq[1:], "esc"))
        elif ch == " ":
            keys.append("space")
        elif ch:
            keys.append(ch.lower())
    return keys


def run() -> None:
    """실시간 루프. 터미널을 raw 모드로 바꿔 한 글자씩 읽는다."""

    if not sys.stdin.isatty():
        print("통합 터미널에서 실행하세요: python3 fps/fps.py")
        return
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        game = Game()
        last = time.monotonic()
        message = "WAVE 1 시작! 적을 전멸시키세요."
        while not game.over:
            now = time.monotonic()
            dt = min(now - last, 0.1)
            last = now
            game.flash = max(0.0, game.flash - dt)
            for key in read_keys():
                if key == "q":
                    game.over = True
                elif key == "w":
                    game.step(1, 0)
                elif key == "s":
                    game.step(-1, 0)
                elif key == "a":
                    game.step(0, -1)
                elif key == "d":
                    game.step(0, 1)
                elif key in ("left", "j"):
                    game.turn_step(-1)
                elif key in ("right", "l"):
                    game.turn_step(1)
                elif key == "space":
                    message = game.shoot()
            game.update_enemies(dt)
            screen, _ = game.render()
            aim = game.aim_info()
            sys.stdout.write("\033[H" + screen + f"\n{message}" + (f"  {aim}" if aim else ""))
            sys.stdout.flush()
            time.sleep(max(0, 1 / FPS - (time.monotonic() - now)))
        sys.stdout.write("\033[2J\033[H")
        if game.won:
            print(f"🏆 전설! 5웨이브 클리어! 점수 {game.score}")
        else:
            print(f"💀 전사... WAVE {game.wave}, 점수 {game.score}")
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


if __name__ == "__main__":
    run()
