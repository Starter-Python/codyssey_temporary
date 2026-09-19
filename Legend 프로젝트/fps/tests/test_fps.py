"""Legend FPS 테스트 | 광선·이동·전투 검증."""

import math
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from fps import ENEMY_HP, Game, cast_ray, parse_map, shade


class RayTest(unittest.TestCase):
    def test_straight_wall_distance(self) -> None:
        grid = ["#####", "#...#", "#...#", "#####"]
        dist, side, wall = cast_ray(grid, 1.5, 2.0, 1.0, 0.0)
        self.assertAlmostEqual(dist, 2.5, places=5)
        self.assertEqual(wall, "#")

    def test_diagonal_hits_wall(self) -> None:
        grid = ["#####", "#...#", "#...#", "#####"]
        dist, _, _ = cast_ray(grid, 1.5, 1.5, 1.0, 1.0)
        self.assertGreater(dist, 0)

    def test_shade_near_darker(self) -> None:
        self.assertEqual(shade(1.0), "█")
        self.assertEqual(shade(10.0), "·")

    def test_parse_map_extracts_spawns(self) -> None:
        grid, start, spawns = parse_map(["#####", "#P E#", "#####"])
        self.assertEqual(start, (1.5, 1.5))
        self.assertEqual(spawns, [(3.5, 1.5)])
        self.assertEqual(grid[1][1], ".")


class MoveTest(unittest.TestCase):
    def test_wall_blocks_movement(self) -> None:
        game = Game()
        game.px, game.py = 1.5, 1.5
        game.angle = math.pi
        before = (game.px, game.py)
        game.move(1, 0, 1.0)
        self.assertEqual(game.px, 1.5)
        self.assertAlmostEqual(game.py, 1.5)

    def test_open_moves_player(self) -> None:
        game = Game()
        game.px, game.py = 1.5, 1.5
        game.angle = 0.0
        game.move(1, 0, 0.5)
        self.assertGreater(game.px, 1.5)


def place_duel(game: Game) -> object:
    """플레이어를 적 옆 빈칸에 세우고 적을 반환한다."""

    for foe in game.enemies:
        if not foe.alive:
            continue
        for dx, dy, ang in ((2.0, 0.0, math.pi), (-2.0, 0.0, 0.0), (0.0, 2.0, -math.pi / 2), (0.0, -2.0, math.pi / 2)):
            px, py = foe.x + dx, foe.y + dy
            mid = (foe.x + dx / 2, foe.y + dy / 2)
            if not game.solid(px, py) and not game.solid(*mid):
                game.px, game.py = px, py
                game.angle = ang
                return foe
    raise AssertionError("duel spot not found")


class CombatTest(unittest.TestCase):
    def test_three_hits_kill(self) -> None:
        game = Game()
        foe = place_duel(game)
        hits = 0
        while foe.alive and hits < 10:
            game.shoot()
            hits += 1
        self.assertFalse(foe.alive)
        self.assertEqual(hits, 3)

    def test_enemy_chases_player(self) -> None:
        game = Game()
        foe = place_duel(game)
        before = abs(foe.x - game.px) + abs(foe.y - game.py)
        game.update_enemies(0.5)
        after = abs(foe.x - game.px) + abs(foe.y - game.py)
        self.assertLess(after, before)

    def test_enemy_attack_kills_at_zero_hp(self) -> None:
        game = Game()
        foe = next(e for e in game.enemies if e.alive)
        foe.x, foe.y = game.px + 0.5, game.py
        foe.cool = 0.0
        game.hp = 1
        game.update_enemies(0.1)
        self.assertTrue(game.over)

    def test_wave_progresses_to_win(self) -> None:
        game = Game()
        self.assertEqual(game.wave, 1)
        for enemy in list(game.enemies):
            enemy.hp = 0
        game._wave_cleared()
        self.assertEqual(game.wave, 2)

    def test_render_and_zbuffer(self) -> None:
        game = Game()
        screen, zbuf = game.render()
        self.assertIn("\033[1;33m+\033[0m", screen)
        self.assertEqual(screen.count("\033[1;33m+\033[0m"), 1)
        self.assertEqual(len(zbuf), 72)
        self.assertTrue(all(d > 0 for d in zbuf))

    def test_score_save(self) -> None:
        game = Game()
        game.score = 500
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "s.json"
            scores = game.save_score("테스터", path)
        self.assertEqual(scores[0]["name"], "테스터")


if __name__ == "__main__":
    unittest.main()
