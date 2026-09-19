"""Legend FPS GUI | tkinter 그래픽 FPS. 표준 라이브러리만 사용.

실행:  cd "Legend 프로젝트/fps" && python3 gui.py
조작:  W/S 이동, A/D 옆걸음, ←/→ 회전, 마우스로 조준, 클릭/Space 발사.
"""

from __future__ import annotations

import math
import time

from fps import FINAL_WAVE, FOV, Game

VIEW_W, VIEW_H = 640, 400
COLS = 320
PANEL_H = 90
FPS_TARGET = 30
MOUSE_SENS = 2.2

WALL_BASE = {"#": (150, 150, 150), "B": (200, 90, 90), "W": (200, 170, 100)}


def shade_color(base: tuple[int, int, int], dist: float) -> str:
    """거리에 따라 어두워지는 색을 만든다."""

    factor = max(0.15, min(1.0, 1.6 / (dist + 0.4)))
    r, g, b = (int(c * factor) for c in base)
    return f"#{r:02x}{g:02x}{b:02x}"


def project_enemy(game: Game, enemy, dir_x: float, dir_y: float, plane_x: float, plane_y: float) -> tuple[float, float, float] | None:
    """적의 화면 위치를 계산한다. (화면x비율, 거리, 크기)"""

    inv = 1.0 / (plane_x * dir_y - dir_x * plane_y)
    rel_x, rel_y = enemy.x - game.px, enemy.y - game.py
    trans_y = inv * (-plane_y * rel_x + plane_x * rel_y)
    if trans_y < 0.2:
        return None
    trans_x = inv * (dir_y * rel_x - dir_x * rel_y)
    return 0.5 * (1 + trans_x / trans_y), trans_y, VIEW_H / trans_y


def steer_from_mouse(mx: int, width: int) -> float:
    """마우스 x좌표를 회전 속도(-1~1)로 바꾼다. 가운데는 정지."""

    return max(-1.0, min(1.0, (mx - width / 2) / (width / 2)))


class Renderer:
    """tkinter Canvas에 그린다. 테스트에선 가짜 캔버스를 받는다."""

    def __init__(self, canvas, width: int = VIEW_W, height: int = VIEW_H) -> None:
        self.cv = canvas
        self.width = width
        self.height = height

    def draw(self, game: Game) -> None:
        cv = self.cv
        cv.delete("all")
        dir_x, dir_y = math.cos(game.angle), math.sin(game.angle)
        plane_x, plane_y = -dir_y * math.tan(FOV / 2), dir_x * math.tan(FOV / 2)
        col_w = self.width / COLS
        zbuf: list[float] = []
        self._ceiling_floor()
        for col in range(COLS):
            cam = 2 * col / COLS - 1
            rdx, rdy = dir_x + plane_x * cam, dir_y + plane_y * cam
            from fps import cast_ray

            dist, side, wall = cast_ray(game.grid, game.px, game.py, rdx, rdy)
            zbuf.append(dist)
            height = min(self.height, int(self.height / dist))
            top = self.height // 2 - height // 2
            base = WALL_BASE.get(wall, (150, 150, 150))
            if side == 1:
                base = tuple(int(c * 0.7) for c in base)
            color = shade_color(base, dist)
            x0 = col * col_w
            cv.create_rectangle(x0, top, x0 + col_w + 1, top + height, fill=color, outline="")
        self._sprites(game, zbuf, dir_x, dir_y, plane_x, plane_y)
        cx = self.width / 2
        cv.create_line(cx - 8, self.height / 2, cx + 8, self.height / 2, fill="yellow", width=2)
        cv.create_line(cx, self.height / 2 - 8, cx, self.height / 2 + 8, fill="yellow", width=2)
        self._hud(game)

    def _ceiling_floor(self) -> None:
        bands = 6
        for i in range(bands):
            f = 1 - i / bands
            ceil = f"#{int(10 + 20 * f):02x}{int(10 + 20 * f):02x}{int(30 + 25 * f):02x}"
            self.cv.create_rectangle(0, i * self.height // 2 // bands, self.width, (i + 1) * self.height // 2 // bands, fill=ceil, outline="")
            fl = f"#{int(15 + 25 * (1 - f)):02x}{int(30 + 20 * (1 - f)):02x}{int(15 + 20 * (1 - f)):02x}"
            y0 = self.height // 2 + i * self.height // 2 // bands
            self.cv.create_rectangle(0, y0, self.width, y0 + self.height // 2 // bands, fill=fl, outline="")

    def _sprites(self, game: Game, zbuf: list[float], dir_x: float, dir_y: float, plane_x: float, plane_y: float) -> None:
        order = sorted(
            (e for e in game.enemies if e.alive),
            key=lambda e: (e.x - game.px) ** 2 + (e.y - game.py) ** 2,
            reverse=True,
        )
        for enemy in order:
            proj = project_enemy(game, enemy, dir_x, dir_y, plane_x, plane_y)
            if proj is None:
                continue
            sx_ratio, dist, size = proj
            screen_x = sx_ratio * self.width
            stripe = int(sx_ratio * COLS)
            if not (0 <= stripe < COLS and dist < zbuf[stripe] + 0.1):
                continue
            w = max(4, size / 3)
            top = self.height / 2 - size / 2
            self.cv.create_rectangle(screen_x - w, top + size * 0.18, screen_x + w, top + size, fill="red", outline="darkred")
            self.cv.create_oval(screen_x - w * 0.5, top, screen_x + w * 0.5, top + size * 0.3, fill="orange", outline="")

    def _hud(self, game: Game) -> None:
        y0 = self.height + 8
        self.cv.create_text(8, y0, anchor="nw", fill="white", font=("Helvetica", 13),
                            text=f"WAVE {game.wave}/{FINAL_WAVE}  HP {game.hp}/{game.max_hp}  점수 {game.score}  처치 {game.kills}")
        self.cv.create_rectangle(8, y0 + 24, 208, y0 + 40, outline="white")
        self.cv.create_rectangle(8, y0 + 24, 8 + 200 * game.hp / game.max_hp, y0 + 40, fill="red", outline="")
        aim = game.aim_info()
        if aim:
            self.cv.create_text(self.width - 8, y0, anchor="ne", fill="yellow", font=("Helvetica", 13), text=aim)
        self._minimap(game, y0)

    def _minimap(self, game: Game, y0: int) -> None:
        cell, ox, oy = 5, self.width - 130, y0 + 22
        gx, gy = int(game.px), int(game.py)
        for y in range(max(0, gy - 6), min(len(game.grid), gy + 7)):
            for x in range(max(0, gx - 8), min(len(game.grid[0]), gx + 9)):
                if (x, y) == (gx, gy):
                    color = "yellow"
                elif any(e.alive and int(e.x) == x and int(e.y) == y for e in game.enemies):
                    color = "red"
                elif game.grid[y][x] != ".":
                    color = "gray"
                else:
                    continue
                self.cv.create_rectangle(ox + (x - gx + 8) * cell, oy + (y - gy + 6) * cell,
                                         ox + (x - gx + 8) * cell + cell - 1, oy + (y - gy + 6) * cell + cell - 1,
                                         fill=color, outline="")


def run_gui() -> None:
    """tkinter 창을 열고 실시간 루프를 돌린다."""

    try:
        import tkinter as tk
    except ImportError:
        print("tkinter가 없습니다. 맥에서는 아래 한 줄로 설치됩니다:")
        print("  brew install python-tk@3.12")
        print("설치 후 다시 실행하세요: python3 gui.py")
        return

    game = Game()
    root = tk.Tk()
    root.title("Legend FPS - 깊은 심연")
    canvas = tk.Canvas(root, width=VIEW_W, height=VIEW_H + PANEL_H, bg="black", highlightthickness=0)
    canvas.pack()
    renderer = Renderer(canvas)
    held: set[str] = set()
    mouse_x = [VIEW_W / 2]

    def on_key_down(event) -> None:
        held.add(event.keysym.lower())

    def on_key_up(event) -> None:
        held.discard(event.keysym.lower())

    def on_motion(event) -> None:
        mouse_x[0] = event.x

    def on_click(_event) -> None:
        message[0] = game.shoot()

    message = ["WAVE 1 시작! 마우스로 조준하고 클릭하세요."]
    root.bind("<KeyPress>", on_key_down)
    root.bind("<KeyRelease>", on_key_up)
    root.bind("<Motion>", on_motion)
    root.bind("<Button-1>", on_click)
    last = [time.monotonic()]

    def tick() -> None:
        now = time.monotonic()
        dt = min(now - last[0], 0.1)
        last[0] = now
        if "w" in held:
            game.step(1, 0)
        if "s" in held:
            game.step(-1, 0)
        if "a" in held:
            game.step(0, -1)
        if "d" in held:
            game.step(0, 1)
        if "left" in held or "j" in held:
            game.turn_step(-1)
        if "right" in held or "l" in held:
            game.turn_step(1)
        if "space" in held:
            message[0] = game.shoot()
            held.discard("space")
        steer = steer_from_mouse(mouse_x[0], VIEW_W)
        if abs(steer) > 0.12:
            game.angle += steer * 2.0 * dt
        game.update_enemies(dt)
        if game.over:
            if game.won:
                message[0] = f"🏆 전설! 5웨이브 클리어! 점수 {game.score}"
            else:
                message[0] = f"💀 전사... WAVE {game.wave}, 점수 {game.score}"
            renderer.draw(game)
            canvas.create_text(VIEW_W / 2, VIEW_H / 2, fill="yellow", font=("Helvetica", 24), text=message[0])
            root.after(3000, root.destroy)
            return
        renderer.draw(game)
        canvas.create_text(8, VIEW_H + PANEL_H - 8, anchor="sw", fill="white", font=("Helvetica", 11), text=message[0])
        root.after(int(1000 / 30), tick)

    tick()
    root.mainloop()


if __name__ == "__main__":
    run_gui()
