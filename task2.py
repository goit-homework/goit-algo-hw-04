"""
Сніжинка Коха через turtle.

Користувач вводить рівень рекурсії. Кількість сегментів = 3 * 4^level,
тому вище 6 turtle малює дуже довго — питаємо підтвердження.

Запуск:
    python3 task2.py
"""

import turtle


def ask_level() -> int:
    """Питаємо рівень. Якщо >6 — перепитуємо."""
    while True:
        raw = input("Рівень рекурсії (рекомендовано 3-6): ").strip()
        try:
            level = int(raw)
        except ValueError:
            print("  треба число")
            continue

        if level < 0:
            print("  рівень не може бути від'ємним")
            continue

        if level > 6:
            confirm = input(
                f"  рівень {level} = {3 * 4**level} сегментів, малювання займе багато часу. Точно? (y/N): "
            ).strip().lower()
            if confirm != "y":
                continue

        return level


def koch_segment(t: turtle.Turtle, length: float, level: int) -> None:
    """Рекурсивна частина: малює один сегмент сніжинки."""
    if level == 0:
        t.forward(length)
        return

    new_len = length / 3
    koch_segment(t, new_len, level - 1)
    t.left(60)
    koch_segment(t, new_len, level - 1)
    t.right(120)
    koch_segment(t, new_len, level - 1)
    t.left(60)
    koch_segment(t, new_len, level - 1)


def setup_interactions(screen: turtle.TurtleScreen) -> None:
    """Скрол-колесо = зум, ЛКМ-перетягування = пан, q = вихід."""
    canvas = screen.getcanvas()

    def zoom(factor: float, x: int, y: int) -> None:
        cx = canvas.canvasx(x)
        cy = canvas.canvasy(y)
        canvas.scale("all", cx, cy, factor, factor)

    # macOS/Windows
    canvas.bind("<MouseWheel>", lambda e: zoom(1.1 if e.delta > 0 else 1 / 1.1, e.x, e.y))
    # Linux X11
    canvas.bind("<Button-4>", lambda e: zoom(1.1, e.x, e.y))
    canvas.bind("<Button-5>", lambda e: zoom(1 / 1.1, e.x, e.y))

    # drag-to-pan
    canvas.bind("<ButtonPress-1>", lambda e: canvas.scan_mark(e.x, e.y))
    canvas.bind("<B1-Motion>", lambda e: canvas.scan_dragto(e.x, e.y, gain=1))

    # вихід
    canvas.bind_all("<KeyPress-q>", lambda _: canvas.winfo_toplevel().destroy())
    canvas.focus_set()


def draw_snowflake(level: int, size: float = 400) -> None:
    screen = turtle.Screen()
    screen.title(f"Сніжинка Коха — рівень {level}  (scroll = zoom, drag = pan, q = вихід)")
    screen.tracer(0)  # вимикаємо анімацію, інакше високі рівні незручні

    t = turtle.Turtle()
    t.hideturtle()
    t.pensize(1)
    t.speed(0)

    # центруємо: стартуємо лівіше і вище, щоб трикутник вийшов посередині
    t.penup()
    t.goto(-size / 2, size / 3)
    t.pendown()

    for _ in range(3):
        koch_segment(t, size, level)
        t.right(120)

    screen.update()
    setup_interactions(screen)

    print("малювання завершено. Scroll = зум, ЛКМ + перетягування = пан, q = вихід.")
    turtle.mainloop()


if __name__ == "__main__":
    print("Сніжинка Коха")
    print("-" * 30)
    level = ask_level()
    draw_snowflake(level)
