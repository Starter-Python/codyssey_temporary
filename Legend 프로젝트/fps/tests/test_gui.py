"""Legend FPS GUI 테스트 | stub 캔버스로 렌더러 검증 (tkinter 불필요)."""

import unittest

from fps import Game
from gui import Renderer, project_enemy, shade_color, steer_from_mouse


class StubCanvas:
    def __init__(self) -> None:
        self.calls = []

    def delete(self, *_args) -> None:
        pass

    def create_rectangle(self, *args, **kwargs) -> None:
        self.calls.append(("rect", args, kwargs))

    def create_oval(self, *args, **kwargs) -> None:
        self.calls.append(("oval", args, kwargs))

    def create_line(self, *args, **kwargs) -> None:
        self.calls.append(("line", args, kwargs))

    def create_text(self, *args, **kwargs) -> None:
        self.calls.append(("text", args, kwargs))


class GuiMathTest(unittest.TestCase):
    def test_shade_near_brighter(self) -> None:
        near = shade_color((150, 150, 150), 1.0)
        far = shade_color((150, 150, 150), 10.0)
        self.assertNotEqual(near, far)
        self.assertTrue(near.startswith("#") and len(near) == 7)

    def test_steer_center_zero_edges_full(self) -> None:
        self.assertAlmostEqual(steer_from_mouse(320, 640), 0.0)
        self.assertAlmostEqual(steer_from_mouse(0, 640), -1.0)
        self.assertAlmostEqual(steer_from_mouse(640, 640), 1.0)

    def test_project_ahead_returns_values(self) -> None:
        import math

        game = Game()
        foe = next(e for e in game.enemies if e.alive)
        game.px, game.py = foe.x - 2.0, foe.y
        if game.solid(game.px, game.py):
            game.px, game.py = foe.x + 2.0, foe.y
        game.angle = math.atan2(foe.y - game.py, foe.x - game.px)
        dx, dy = math.cos(game.angle), math.sin(game.angle)
        proj = project_enemy(game, foe, dx, dy, -dy * 0.66, dx * 0.66)
        self.assertIsNotNone(proj)
        assert proj is not None
        ratio, dist, size = proj
        self.assertGreater(dist, 0)
        self.assertGreater(size, 0)


class RendererTest(unittest.TestCase):
    def test_draw_produces_wall_columns(self) -> None:
        game = Game()
        stub = StubCanvas()
        Renderer(stub).draw(game)
        rects = [c for c in stub.calls if c[0] == "rect"]
        self.assertGreaterEqual(len(rects), 320)
        texts = [c for c in stub.calls if c[0] == "text"]
        self.assertTrue(any("WAVE" in str(c[1]) + str(c[2]) for c in texts))

    def test_draw_shows_enemy_sprite(self) -> None:
        import math

        game = Game()
        foe = next(e for e in game.enemies if e.alive)
        game.px, game.py = foe.x - 2.0, foe.y
        if game.solid(game.px, game.py):
            self.skipTest("no open duel spot")
        game.angle = 0.0
        stub = StubCanvas()
        Renderer(stub).draw(game)
        ovals = [c for c in stub.calls if c[0] == "oval"]
        self.assertGreater(len(ovals), 0)


if __name__ == "__main__":
    unittest.main()
