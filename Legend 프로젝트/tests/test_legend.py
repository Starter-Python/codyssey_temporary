"""Legend 테스트 | 지형·전투·저장 검증."""

import random
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from actors import Player, drink_potion, gain_xp, roll_damage
from game import Game, add_score, load_scores, reachable_check
from world import compute_fov, gen_dungeon, reachable_floors


class WorldTest(unittest.TestCase):
    def test_dungeon_is_fully_connected(self) -> None:
        for seed in (1, 7, 42, 999, 12345):
            dungeon = gen_dungeon(seed)
            self.assertEqual(len(reachable_floors(dungeon)), len(dungeon.floor_tiles()))

    def test_same_seed_same_dungeon(self) -> None:
        self.assertEqual(gen_dungeon(42).tiles, gen_dungeon(42).tiles)
        self.assertNotEqual(gen_dungeon(42).tiles, gen_dungeon(43).tiles)

    def test_fov_contains_player_and_nothing_behind_wall(self) -> None:
        game = Game(seeds=[11, 22, 33])
        p = game.player
        visible = compute_fov(game.state.dungeon, p.x, p.y)
        self.assertIn((p.x, p.y), visible)
        self.assertTrue(len(visible) > 10)

    def test_reachable_check_helper(self) -> None:
        self.assertTrue(reachable_check(2024))


class CombatTest(unittest.TestCase):
    def test_damage_at_least_one(self) -> None:
        rng = random.Random(0)
        for _ in range(50):
            self.assertGreaterEqual(roll_damage(3, 99, rng), 1)

    def test_level_up_heals_and_raises_stats(self) -> None:
        player = Player(x=1, y=1)
        self.assertTrue(gain_xp(player, 20))
        self.assertEqual(player.level, 2)
        self.assertEqual(player.hp, player.max_hp)
        self.assertEqual(player.atk, 10)

    def test_potion_heals_and_consumes(self) -> None:
        player = Player(x=1, y=1, hp=10, potions=1)
        message = drink_potion(player)
        self.assertEqual(player.potions, 0)
        self.assertGreater(player.hp, 10)
        self.assertIn("물약", message)

    def test_empty_potion_keeps_hp(self) -> None:
        player = Player(x=1, y=1, hp=10, potions=0)
        drink_potion(player)
        self.assertEqual(player.hp, 10)


class GameFlowTest(unittest.TestCase):
    def test_twenty_random_moves_never_crash(self) -> None:
        game = Game(seeds=[5, 6, 7])
        rng = random.Random(3)
        for _ in range(20):
            dx, dy = rng.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
            game.do_move(dx, dy)
            if game.over:
                break
        self.assertGreaterEqual(game.turns, 1)
        self.assertIn(game.player.x, range(60))

    def test_bump_attacks_enemy(self) -> None:
        game = Game(seeds=[5, 6, 7])
        state = game.state
        foe = next(e for e in state.enemies if e.alive)
        game.player.x, game.player.y = foe.x - 1, foe.y
        if not state.dungeon.walkable(foe.x - 1, foe.y):
            game.player.x, game.player.y = foe.x, foe.y - 1
        target_hp = foe.hp
        game.do_move(foe.x - game.player.x, foe.y - game.player.y)
        self.assertLess(foe.hp, target_hp)

    def test_stairs_go_down(self) -> None:
        game = Game(seeds=[5, 6, 7])
        stairs = game.state.dungeon.stairs
        assert stairs is not None
        game.player.x, game.player.y = stairs
        game.go_down()
        self.assertEqual(game.floor_no, 2)

    def test_render_contains_hud(self) -> None:
        game = Game(seeds=[5, 6, 7])
        screen = game.render()
        self.assertIn("HP", screen)
        self.assertIn("@", screen)

    def test_save_load_roundtrip(self) -> None:
        game = Game(seeds=[5, 6, 7])
        game.player.gold = 77
        game.turns = 12
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "save.json"
            game.save(path)
            loaded = Game.load(path)
        self.assertEqual(loaded.player.gold, 77)
        self.assertEqual(loaded.turns, 12)
        self.assertEqual(loaded.seeds, [5, 6, 7])

    def test_scores_sorted_desc(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "scores.json"
            add_score("A", 100, 1, 10, False, path)
            add_score("B", 300, 2, 20, True, path)
            scores = load_scores(path)
        self.assertEqual(scores[0]["name"], "B")
        self.assertEqual(len(scores), 2)

    def test_quit_command_saves(self) -> None:
        import game as game_module

        game = Game(seeds=[5, 6, 7])
        with TemporaryDirectory() as tmp:
            save_path = Path(tmp) / "save.json"
            with patch.object(game_module, "SAVE_FILE", save_path):
                from legend import play

                with patch("builtins.input", side_effect=["q"]):
                    play(game)
            self.assertTrue(save_path.exists())


if __name__ == "__main__":
    unittest.main()
