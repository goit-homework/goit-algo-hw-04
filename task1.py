"""
Рекурсивний сортувальник файлів по розширенню.

Бере source-директорію, проходить рекурсивно, копіює кожен файл
у dest/<розширення>/. Колізії імен розв'язуються через суфікс __1, __2, ...
Файли без розширення йдуть у no_ext/.

Запуск:
    python3 task1.py <source> [dest]

Якщо dest не вказано — використовується ./dist
"""

import argparse
import shutil
import sys
from collections import Counter
from pathlib import Path


def parse_args() -> tuple[Path, Path]:
    parser = argparse.ArgumentParser(description="Рекурсивно сортує файли по розширенню")
    parser.add_argument("source", type=Path, help="директорія-джерело")
    parser.add_argument(
        "dest",
        type=Path,
        nargs="?",
        default=Path("dist"),
        help="директорія призначення (за замовчуванням ./dist)",
    )
    args = parser.parse_args()
    return args.source, args.dest


def resolve_collision(target: Path) -> Path:
    """Якщо target уже існує — додаємо __1, __2 ... поки не знайдемо вільну назву."""
    if not target.exists():
        return target

    stem, suffix = target.stem, target.suffix
    n = 1
    while True:
        candidate = target.with_name(f"{stem}__{n}{suffix}")
        if not candidate.exists():
            return candidate
        n += 1


def bucket_for(file: Path) -> str:
    ext = file.suffix.lstrip(".").lower()
    return ext if ext else "no_ext"


def copy_recursive(src: Path, dest: Path, stats: Counter) -> None:
    """Рекурсивно проходить src і копіює файли у dest/<bucket>/."""
    try:
        entries = list(src.iterdir())
    except PermissionError as e:
        print(f"  [skip] немає доступу до {src}: {e}", file=sys.stderr)
        return
    except OSError as e:
        print(f"  [skip] помилка читання {src}: {e}", file=sys.stderr)
        return

    for entry in entries:
        if entry.is_symlink():
            # пропускаємо симлінки, бо можна впасти в нескінченний цикл
            print(f"  [skip] symlink: {entry}")
            continue

        if entry.is_dir():
            copy_recursive(entry, dest, stats)
            continue

        if not entry.is_file():
            continue

        bucket = bucket_for(entry)
        target_dir = dest / bucket
        try:
            target_dir.mkdir(parents=True, exist_ok=True)
            target = resolve_collision(target_dir / entry.name)
            shutil.copy2(entry, target)
            stats[bucket] += 1
            print(f"  [copy] {entry}  ->  {target}")
        except (OSError, shutil.Error) as e:
            print(f"  [fail] {entry}: {e}", file=sys.stderr)


def print_summary(stats: Counter, dest: Path) -> None:
    print()
    print("=" * 50)
    if not stats:
        print(f"  нічого не скопійовано в {dest}")
    else:
        total = sum(stats.values())
        print(f"  скопійовано в {dest}:")
        for ext, count in sorted(stats.items(), key=lambda x: (-x[1], x[0])):
            label = ext if ext == "no_ext" else f".{ext}"
            print(f"    {label:<11} {count:>5}")
        print(f"  всього файлів: {total}")
    print("=" * 50)


def main() -> int:
    source, dest = parse_args()

    if not source.exists():
        print(f"помилка: джерело не існує: {source}", file=sys.stderr)
        return 1
    if not source.is_dir():
        print(f"помилка: джерело не є директорією: {source}", file=sys.stderr)
        return 1

    # запобігаємо ситуації коли dest всередині source — інакше копіюємо саме в себе
    try:
        src_resolved = source.resolve()
        dst_resolved = dest.resolve()
        if dst_resolved == src_resolved or src_resolved in dst_resolved.parents:
            print("помилка: dest не може бути всередині source", file=sys.stderr)
            return 1
    except OSError:
        pass

    print(f"джерело:    {source}")
    print(f"призначення: {dest}")
    print("-" * 50)

    stats: Counter = Counter()
    copy_recursive(source, dest, stats)
    print_summary(stats, dest)
    return 0


if __name__ == "__main__":
    sys.exit(main())
