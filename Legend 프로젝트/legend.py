"""Legend | 깊은 심연의 던전 크롤러 실행 파일."""

from __future__ import annotations

import sys

from game import SAVE_FILE, Game, add_score, load_scores

TITLE = """\033[1;35m
   ██╗     ███████╗ ██████╗ ███████╗███╗   ██╗██████╗
   ██║     ██╔════╝██╔════╝ ██╔════╝████╗  ██║██╔══██╗
   ██║     █████╗  ██║  ███╗█████╗  ██╔██╗ ██║██║  ██║
   ██║     ██╔══╝  ██║   ██║██╔══╝  ██║╚██╗██║██║  ██║
   ███████╗███████╗╚██████╔╝███████╗██║ ╚████║██████╔╝
   ╚══════╝╚══════╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝╚═════╝
   \033[0m   -- 깊은 심연의 던전 크롤러 --
   3층 보스 드래곤을 무찌르는 자, 전설이 되리라.
"""


def show_scores() -> None:
    """명예의 전당 10위를 출력한다."""

    scores = load_scores()
    print("\n[ 명예의 전당 Top 10 ]")
    if not scores:
        print("아직 기록이 없습니다. 첫 전설의 주인공이 되어 보세요!")
        return
    for i, s in enumerate(scores, 1):
        mark = "🏆" if s.get("won") else "💀"
        print(f"{i}. {mark} {s['name']} - {s['score']}점 ({s['floor']}층, {s['turns']}턴)")


def play(game: Game) -> None:
    """한 판의 게임 루프를 돌린다."""

    while not game.over:
        print(game.render())
        try:
            cmd = input("명령> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\n심연에서 탈출합니다...")
            return
        if cmd in ("w", "a", "s", "d"):
            dx, dy = {"w": (0, -1), "s": (0, 1), "a": (-1, 0), "d": (1, 0)}[cmd]
            game.do_move(dx, dy)
        elif cmd == "e":
            game.say(drink(game))
        elif cmd in (">", "g"):
            game.go_down()
        elif cmd == "i":
            p = game.player
            game.say(f"상태: Lv.{p.level} HP {p.hp}/{p.max_hp} 공{p.total_atk} 방{p.total_def} 골드{p.gold}")
        elif cmd == "h":
            from game import HELP

            game.say(HELP)
        elif cmd == "q":
            game.save()
            print("저장했습니다. 다음에 이어서 도전하세요!")
            return
        else:
            game.say("알 수 없는 명령입니다. h를 눌러 도움말을 보세요.")
    print(game.render())
    if game.won:
        print(f"\n🏆 전설 달성! 드래곤을 무찔렀습니다! 점수: {game.score}점")
    else:
        print(f"\n💀 당신은 심연에 잠들었습니다... 점수: {game.score}점")
    try:
        name = input("이름을 남기세요 (Enter=무명용사): ").strip() or "무명용사"
    except (EOFError, KeyboardInterrupt):
        name = "무명용사"
    add_score(name, game.score, game.floor_no, game.turns, game.won)
    show_scores()
    if SAVE_FILE.exists():
        SAVE_FILE.unlink()


def drink(game: Game) -> str:
    """물약 결과를 반환한다 (테스트에서 재사용)."""

    from actors import drink_potion

    return drink_potion(game.player)


def main() -> None:
    """메인 메뉴를 보여주고 선택을 실행한다."""

    while True:
        print(TITLE)
        print("1. 새 모험 시작")
        print("2. 이어하기")
        print("3. 명예의 전당")
        print("4. 종료")
        try:
            choice = input("선택> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n안녕히 가세요, 용사여.")
            return
        if choice == "1":
            play(Game())
        elif choice == "2":
            try:
                play(Game.load())
            except (FileNotFoundError, ValueError, OSError, KeyError):
                print("저장 파일이 없거나 깨졌습니다. 새 모험을 시작하세요.")
        elif choice == "3":
            show_scores()
        elif choice == "4":
            print("안녕히 가세요, 용사여.")
            return
        else:
            print("1~4를 입력하세요.")


if __name__ == "__main__":
    sys.exit(main())
