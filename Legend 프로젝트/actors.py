"""Legend | 플레이어·몬스터와 전투 공식."""

from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass
class Player:
    """플레이어 상태. 저장·불러오기의 단위다."""

    x: int
    y: int
    hp: int = 40
    max_hp: int = 40
    atk: int = 8
    defense: int = 2
    level: int = 1
    xp: int = 0
    xp_next: int = 20
    potions: int = 2
    gold: int = 0
    kills: int = 0
    weapon: str = "낡은 검"
    weapon_bonus: int = 0
    armor: str = "천 옷"
    armor_bonus: int = 0

    @property
    def total_atk(self) -> int:
        return self.atk + self.weapon_bonus

    @property
    def total_def(self) -> int:
        return self.defense + self.armor_bonus

    def to_dict(self) -> dict:
        return self.__dict__.copy()

    @classmethod
    def from_dict(cls, data: dict) -> Player:
        player = cls(x=int(data.get("x", 1)), y=int(data.get("y", 1)))
        for key in player.__dict__:
            if key in data:
                setattr(player, key, data[key])
        return player


@dataclass
class Enemy:
    """몬스터 1마리."""

    name: str
    symbol: str
    x: int
    y: int
    hp: int
    max_hp: int
    atk: int
    defense: int
    xp: int
    gold: int
    is_boss: bool = False

    @property
    def alive(self) -> bool:
        return self.hp > 0


# 이름, 심볼, 체력, 공격, 방어, 경험치, 골드
ENEMY_TYPES = {
    "slime": ("슬라임", "S", 8, 3, 0, 8, 3),
    "goblin": ("고블린", "G", 12, 5, 1, 14, 6),
    "orc": ("오크", "O", 20, 7, 2, 24, 10),
    "knight": ("다크나이트", "K", 30, 10, 3, 40, 16),
    "dragon": ("깊은 심연의 드래곤", "D", 80, 14, 4, 150, 100),
}

FLOOR_TABLE = {
    1: ["slime", "slime", "goblin", "goblin", "orc", "orc"],
    2: ["goblin", "goblin", "orc", "orc", "orc", "knight", "knight", "slime"],
    3: ["orc", "orc", "knight", "knight", "goblin", "goblin"],
}

POTION_HEAL = 15
WEAPONS = [("단검", 1), ("철검", 2), ("미스릴검", 4)]
ARMORS = [("가죽 갑옷", 1), ("사슬 갑옷", 2)]


def make_enemy(kind: str, x: int, y: int, floor: int, rng: random.Random) -> Enemy:
    """층 보정을 적용해 몬스터를 생성한다."""

    name, symbol, hp, atk, defense, xp, gold = ENEMY_TYPES[kind]
    bonus = floor - 1
    hp += 4 * bonus
    atk += 1 * bonus
    jitter = rng.randint(0, 2)
    return Enemy(name, symbol, x, y, hp + jitter, hp + jitter, atk, defense, xp, gold)


def make_boss(x: int, y: int) -> Enemy:
    """3층 보스를 생성한다."""

    name, symbol, hp, atk, defense, xp, gold = ENEMY_TYPES["dragon"]
    return Enemy(name, symbol, x, y, hp, hp, atk, defense, xp, gold, is_boss=True)


def roll_damage(atk: int, defense: int, rng: random.Random) -> int:
    """데미지 공식. 최소 1은 보장한다."""

    return max(1, atk - defense + rng.randint(-1, 2))


def gain_xp(player: Player, amount: int) -> bool:
    """경험치를 주고, 레벨업했으면 True를 반환한다."""

    player.xp += amount
    leveled = False
    while player.xp >= player.xp_next:
        player.xp -= player.xp_next
        player.level += 1
        player.xp_next = 25 * player.level
        player.max_hp += 8
        player.hp = player.max_hp
        player.atk += 2
        player.defense += 1
        leveled = True
    return leveled


def drink_potion(player: Player) -> str:
    """물약을 마신다. 결과를 문장으로 반환한다."""

    if player.potions <= 0:
        return "물약이 없습니다!"
    if player.hp >= player.max_hp:
        return "체력이 가득 찼습니다. 물약을 아끼세요."
    player.potions -= 1
    healed = min(POTION_HEAL, player.max_hp - player.hp)
    player.hp += healed
    return f"물약을 마셨습니다. 체력 +{healed} (남은 물약 {player.potions}개)"
