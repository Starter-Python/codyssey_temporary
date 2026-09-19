"""Legend | 게임 진행·렌더링·저장."""
# 깊은 심연의 던전 크롤러. 3층 보스를 잡으면 승리.

from __future__ import annotations

import json
import os
import random
from dataclasses import dataclass, field
from pathlib import Path

from actors import (
    ARMORS,
    FLOOR_TABLE,
    WEAPONS,
    Enemy,
    Player,
    drink_potion,
    gain_xp,
    make_boss,
    make_enemy,
    roll_damage,
)
from world import Dungeon, compute_fov, gen_dungeon, reachable_floors

BASE_DIR = Path(__file__).parent
SAVE_FILE = BASE_DIR / "save.json"
SCORES_FILE = BASE_DIR / "scores.json"

FINAL_FLOOR = 3
VIEW_W, VIEW_H = 31, 17

C = {
    "reset": "\033[0m",
    "wall": "\033[90m",
    "floor": "\033[37m",
    "dim": "\033[2;37m",
    "player": "\033[1;33m",
    "enemy": "\033[1;31m",
    "boss": "\033[1;35m",
    "stairs": "\033[1;36m",
    "item": "\033[1;32m",
    "gold": "\033[1;33m",
    "hp": "\033[1;31m",
    "xp": "\033[1;34m",
    "title": "\033[1;36m",
}

MOVES = {"w": (0, -1), "s": (0, 1), "a": (-1, 0), "d": (1, 0)}

HELP = (
    "w/a/s/d 이동(몬스터에게 부딪히면 공격) | e 물약 | > 아래층으로 | "
    "i 상태 | h 도움말 | q 저장 후 종료"
)


@dataclass
class FloorState:
    """한 층의 실황. 시드·몬스터·아이템·탐험 기록을 묶는다."""

    seed: int
    dungeon: Dungeon
    enemies: list[Enemy] = field(default_factory=list)
    items: dict[tuple[int, int], tuple[str, dict]] = field(default_factory=dict)
    explored: set[tuple[int, int]] = field(default_factory=set)


class Game:
    """던전 3층과 플레이어 상태를 함께 관리한다."""

    def __init__(self, seeds: list[int] | None = None) -> None:
        self.rng = random.Random()
        self.seeds = seeds or [self.rng.randint(1, 999999) for _ in range(FINAL_FLOOR)]
        self.floor_no = 1
        self.floors: dict[int, FloorState] = {}
        start = self._load_floor(1).dungeon.rooms[0].center
        self.player = Player(x=start[0], y=start[1])
        self.turns = 0
        self.messages: list[str] = ["깊은 심연에 오신 것을 환영합니다!"]
        self.over = False
        self.won = False

    # -- 층 생성 ------------------------------------------------------

    def _load_floor(self, floor_no: int) -> FloorState:
        """해당 층 실황을 만들거나 캐시에서 꺼낸다."""

        if floor_no in self.floors:
            return self.floors[floor_no]
        seed = self.seeds[floor_no - 1]
        rng = random.Random(seed + floor_no * 7919)
        dungeon = gen_dungeon(seed)
        state = FloorState(seed=seed, dungeon=dungeon)
        taken = {dungeon.rooms[0].center, dungeon.stairs} if dungeon.stairs else set()

        def free_spot() -> tuple[int, int]:
            spots = [t for t in dungeon.floor_tiles() if t not in taken]
            spot = rng.choice(spots)
            taken.add(spot)
            return spot

        for kind in FLOOR_TABLE[floor_no]:
            x, y = free_spot()
            state.enemies.append(make_enemy(kind, x, y, floor_no, rng))
        if floor_no == FINAL_FLOOR and dungeon.stairs:
            dungeon.stairs = None
            bx, by = dungeon.rooms[-1].center
            state.enemies = [e for e in state.enemies if (e.x, e.y) != (bx, by)]
            state.enemies.append(make_boss(bx, by))
        for _ in range(3):
            x, y = free_spot()
            state.items[(x, y)] = ("potion", {})
        wx, wy = free_spot()
        wname, wbonus = WEAPONS[min(floor_no - 1, len(WEAPONS) - 1)]
        state.items[(wx, wy)] = ("weapon", {"name": wname, "bonus": wbonus})
        ax, ay = free_spot()
        aname, abonus = ARMORS[min(floor_no - 1, len(ARMORS) - 1)]
        state.items[(ax, ay)] = ("armor", {"name": aname, "bonus": abonus})
        self.floors[floor_no] = state
        return state

    @property
    def state(self) -> FloorState:
        return self._load_floor(self.floor_no)

    # -- 렌더링 --------------------------------------------------------

    def render(self) -> str:
        """화면 전체 문자열을 만든다."""

        os.system("")  # Windows ANSI 활성화용 (무해)
        state = self.state
        visible = compute_fov(state.dungeon, self.player.x, self.player.y)
        state.explored |= visible
        foes = {(e.x, e.y): e for e in state.enemies if e.alive}

        x0 = min(max(self.player.x - VIEW_W // 2, 0), state.dungeon.width - VIEW_W)
        y0 = min(max(self.player.y - VIEW_H // 2, 0), state.dungeon.height - VIEW_H)
        out = ["\033[2J\033[H"]
        out.append(f"{C['title']}=== 깊은 심연 {self.floor_no}층 / {FINAL_FLOOR}층 ==={C['reset']}")
        for y in range(y0, y0 + VIEW_H):
            row = []
            for x in range(x0, x0 + VIEW_W):
                if (x, y) == (self.player.x, self.player.y):
                    row.append(f"{C['player']}@{C['reset']}")
                elif (x, y) in foes and (x, y) in visible:
                    foe = foes[(x, y)]
                    color = C["boss"] if foe.is_boss else C["enemy"]
                    row.append(f"{color}{foe.symbol}{C['reset']}")
                elif (x, y) in visible:
                    row.append(self._tile_char(state, x, y, bright=True))
                elif (x, y) in state.explored:
                    row.append(self._tile_char(state, x, y, bright=False))
                else:
                    row.append(" ")
            out.append("".join(row))
        out.append(self._hud())
        out.append("-" * 40)
        out.extend(self.messages[-5:])
        out.append(HELP)
        return "\n".join(out)

    def _tile_char(self, state: FloorState, x: int, y: int, bright: bool) -> str:
        """좌표의 문자(색 포함)를 반환한다."""

        if not state.dungeon.walkable(x, y):
            return f"{C['wall']}#{C['reset']}"
        if state.dungeon.stairs == (x, y):
            return f"{C['stairs']}>{C['reset']}"
        if (x, y) in state.items:
            kind = state.items[(x, y)][0]
            glyph = {"potion": "!", "weapon": "/", "armor": "["}[kind]
            return f"{C['item']}{glyph}{C['reset']}"
        return f"{C['floor']}.{C['reset']}" if bright else f"{C['dim']}.{C['reset']}"

    def _hud(self) -> str:
        """체력·경험치 바와 상태 줄을 만든다."""

        p = self.player
        hp_bar = "█" * (p.hp * 10 // p.max_hp) + "░" * (10 - p.hp * 10 // p.max_hp)
        xp_bar = "█" * min(10, p.xp * 10 // p.xp_next) + "░" * (10 - min(10, p.xp * 10 // p.xp_next))
        return (
            f"{C['hp']}HP [{hp_bar}] {p.hp}/{p.max_hp}{C['reset']}  "
            f"{C['xp']}Lv.{p.level} [{xp_bar}] {p.xp}/{p.xp_next}{C['reset']}\n"
            f"공격 {p.total_atk}({p.weapon}) 방어 {p.total_def}({p.armor}) "
            f"물약 {p.potions} {C['gold']}골드 {p.gold}{C['reset']} "
            f"처치 {p.kills} 턴 {self.turns}"
        )

    # -- 행동 ----------------------------------------------------------

    def say(self, message: str) -> None:
        self.messages.append(message)

    def enemy_at(self, x: int, y: int) -> Enemy | None:
        return next((e for e in self.state.enemies if e.alive and (e.x, e.y) == (x, y)), None)

    def do_move(self, dx: int, dy: int) -> None:
        """한 칸 이동. 몬스터가 있으면 대신 공격한다."""

        p = self.player
        nx, ny = p.x + dx, p.y + dy
        state = self.state
        if not state.dungeon.walkable(nx, ny):
            self.say("벽입니다.")
            return
        foe = self.enemy_at(nx, ny)
        if foe is not None:
            dmg = roll_damage(p.total_atk, foe.defense, self.rng)
            foe.hp -= dmg
            self.say(f"{foe.name}에게 {dmg} 피해!")
            if not foe.alive:
                self._kill(foe)
        else:
            p.x, p.y = nx, ny
            self._pickup()
        self.turns += 1
        self._enemies_act()

    def _kill(self, foe: Enemy) -> None:
        """처치 보상과 승리 판정을 처리한다."""

        p = self.player
        p.kills += 1
        p.gold += foe.gold
        self.say(f"{foe.name} 처치! +{foe.xp}XP, +{foe.gold}골드")
        if gain_xp(p, foe.xp):
            self.say(f"레벨 업! Lv.{p.level} (체력全回復, 공격+2, 방어+1)")
        if foe.is_boss:
            self.won = True
            self.over = True

    def _pickup(self) -> None:
        """발밑 아이템을 줍는다."""

        p = self.player
        pos = (p.x, p.y)
        if pos not in self.state.items:
            return
        kind, info = self.state.items.pop(pos)
        if kind == "potion":
            p.potions += 1
            self.say(f"물약 획득! (총 {p.potions}개)")
        elif kind == "weapon":
            if info["bonus"] > p.weapon_bonus:
                p.weapon, p.weapon_bonus = info["name"], info["bonus"]
                self.say(f"{info['name']} 장착! 공격 +{info['bonus']}")
            else:
                p.gold += 5
                self.say(f"{info['name']}은 약해서 팔았습니다. +5골드")
        elif kind == "armor":
            if info["bonus"] > p.armor_bonus:
                p.armor, p.armor_bonus = info["name"], info["bonus"]
                self.say(f"{info['name']} 장착! 방어 +{info['bonus']}")
            else:
                p.gold += 5
                self.say(f"{info['name']}은 약해서 팔았습니다. +5골드")

    def _enemies_act(self) -> None:
        """모든 몬스터가 한 번씩 행동한다."""

        p = self.player
        for foe in self.state.enemies:
            if not foe.alive:
                continue
            dist = abs(foe.x - p.x) + abs(foe.y - p.y)
            if dist == 1:
                dmg = roll_damage(foe.atk, p.total_def, self.rng)
                p.hp -= dmg
                self.say(f"{foe.name}의 공격! {dmg} 피해.")
                if p.hp <= 0:
                    p.hp = 0
                    self.over = True
                    return
            elif dist <= 7:
                step = self._step_toward(foe, p.x, p.y)
                if step is not None:
                    foe.x, foe.y = step
            elif self.rng.random() < 0.4:
                dx, dy = self.rng.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
                nx, ny = foe.x + dx, foe.y + dy
                if self.state.dungeon.walkable(nx, ny) and self.enemy_at(nx, ny) is None:
                    if (nx, ny) != (p.x, p.y):
                        foe.x, foe.y = nx, ny

    def _step_toward(self, foe: Enemy, tx: int, ty: int) -> tuple[int, int] | None:
        """거리가 줄어드는 빈 칸 중 첫 번째를 반환한다."""

        best = None
        best_dist = abs(foe.x - tx) + abs(foe.y - ty)
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = foe.x + dx, foe.y + dy
            if not self.state.dungeon.walkable(nx, ny):
                continue
            if self.enemy_at(nx, ny) is not None or (nx, ny) == (self.player.x, self.player.y):
                continue
            dist = abs(nx - tx) + abs(ny - ty)
            if dist < best_dist:
                best, best_dist = (nx, ny), dist
        return best

    def go_down(self) -> None:
        """계단에서 아래층으로 내려간다."""

        if self.state.dungeon.stairs != (self.player.x, self.player.y):
            self.say("계단(>) 위에서 눌러야 내려갈 수 있습니다.")
            return
        if self.floor_no >= FINAL_FLOOR:
            self.say("여기가 심연의 끝입니다.")
            return
        self.floor_no += 1
        start = self.state.dungeon.rooms[0].center
        self.player.x, self.player.y = start
        self.say(f"{self.floor_no}층에 내려왔습니다. 더 강한 기운이 느껴집니다...")

    @property
    def score(self) -> int:
        p = self.player
        return self.floor_no * 500 + p.kills * 100 + p.gold * 2 + p.level * 200

    # -- 저장·기록 ------------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "seeds": self.seeds,
            "floor_no": self.floor_no,
            "turns": self.turns,
            "player": self.player.to_dict(),
        }

    def save(self, path: Path | None = None) -> None:
        with open(path or SAVE_FILE, "w", encoding="utf-8") as file:
            json.dump(self.to_dict(), file, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, path: Path = SAVE_FILE) -> Game:
        with open(path, encoding="utf-8") as file:
            data = json.load(file)
        game = cls(seeds=list(data["seeds"]))
        game.floor_no = int(data["floor_no"])
        game.turns = int(data.get("turns", 0))
        game.player = Player.from_dict(data["player"])
        return game


def load_scores(path: Path = SCORES_FILE) -> list[dict]:
    try:
        with open(path, encoding="utf-8") as file:
            data = json.load(file)
        return data if isinstance(data, list) else []
    except (FileNotFoundError, ValueError, OSError):
        return []


def add_score(name: str, score: int, floor: int, turns: int, won: bool, path: Path = SCORES_FILE) -> list[dict]:
    scores = load_scores(path)
    scores.append({"name": name, "score": score, "floor": floor, "turns": turns, "won": won})
    scores.sort(key=lambda s: int(s.get("score", 0)), reverse=True)
    with open(path, "w", encoding="utf-8") as file:
        json.dump(scores[:10], file, ensure_ascii=False, indent=2)
    return scores[:10]


def reachable_check(seed: int) -> bool:
    """지형 연결성 검증용. 바닥 전체가 시작점에서 닿으면 True."""

    dungeon = gen_dungeon(seed)
    return len(reachable_floors(dungeon)) == len(dungeon.floor_tiles())
