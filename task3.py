"""
Бенчмарк трьох сортувань: merge sort, insertion sort, Timsort (sorted()).

Тестуємо на 4 типах розподілу даних і 4 розмірах. Час міряємо через timeit.
Результати: ASCII-таблиця у консоль + графік benchmark.png.

Запуск:
    python3 task3.py
"""

import random
import timeit
from typing import Callable

import matplotlib.pyplot as plt


# ---------- алгоритми ----------

def insertion_sort(arr: list[int]) -> list[int]:
    a = arr[:]
    for i in range(1, len(a)):
        key = a[i]
        j = i - 1
        while j >= 0 and a[j] > key:
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = key
    return a


def merge_sort(arr: list[int]) -> list[int]:
    if len(arr) <= 1:
        return arr[:]
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return _merge(left, right)


def _merge(left: list[int], right: list[int]) -> list[int]:
    out: list[int] = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            out.append(left[i])
            i += 1
        else:
            out.append(right[j])
            j += 1
    out.extend(left[i:])
    out.extend(right[j:])
    return out


def timsort(arr: list[int]) -> list[int]:
    return sorted(arr)


# ---------- генератори датасетів ----------

def gen_random(n: int) -> list[int]:
    return [random.randint(0, n * 10) for _ in range(n)]


def gen_sorted(n: int) -> list[int]:
    return list(range(n))


def gen_reverse(n: int) -> list[int]:
    return list(range(n, 0, -1))


def gen_nearly_sorted(n: int) -> list[int]:
    """Майже відсортований: беремо range і свапаємо ~5% сусідніх пар."""
    data = list(range(n))
    swaps = max(1, n // 20)
    for _ in range(swaps):
        i = random.randint(0, n - 2)
        data[i], data[i + 1] = data[i + 1], data[i]
    return data


DATASETS = {
    "random":        gen_random,
    "sorted":        gen_sorted,
    "reverse":       gen_reverse,
    "nearly_sorted": gen_nearly_sorted,
}

ALGORITHMS: dict[str, Callable[[list[int]], list[int]]] = {
    "insertion": insertion_sort,
    "merge":     merge_sort,
    "timsort":   timsort,
}

SIZES = [100, 1_000, 5_000, 10_000, 100_000]

# на 100k insertion sort O(n²) виходить ~140с на запуск — пропускаємо,
# гепу між алгоритмами вже досить видно на 10k
SKIP = {("insertion", 100_000)}


# ---------- замір часу ----------

def measure(algo: Callable, data: list[int], repeats: int) -> float:
    """Середній час одного запуску в секундах."""
    timer = timeit.Timer(lambda: algo(data))
    total = timer.timeit(number=repeats)
    return total / repeats


def pick_repeats(size: int) -> int:
    """Більше повторів для малих масивів — щоб шум усереднити."""
    if size <= 100:
        return 50
    if size <= 1_000:
        return 10
    if size <= 5_000:
        return 5
    if size <= 10_000:
        return 3
    return 1


# ---------- запуск ----------

def run_benchmark() -> dict[str, dict[str, dict[int, float | None]]]:
    """Структура: results[dataset][algo][size] -> seconds (або None якщо skip)."""
    results: dict[str, dict[str, dict[int, float | None]]] = {
        ds: {algo: {} for algo in ALGORITHMS} for ds in DATASETS
    }

    for ds_name, gen in DATASETS.items():
        print(f"\n[dataset: {ds_name}]")
        for size in SIZES:
            random.seed(42)
            data = gen(size)
            repeats = pick_repeats(size)
            row = f"  n={size:>6}: "
            for algo_name, algo in ALGORITHMS.items():
                if (algo_name, size) in SKIP:
                    results[ds_name][algo_name][size] = None
                    row += f"{algo_name}=    skip    "
                    continue
                t = measure(algo, data, repeats)
                results[ds_name][algo_name][size] = t
                row += f"{algo_name}={t * 1000:8.2f}ms  "
            print(row)
    return results


# ---------- виведення таблиці ----------

def print_table(results: dict) -> None:
    print()
    print("=" * 78)
    print("  Результати (мс на запуск, менше — краще)")
    print("=" * 78)

    header = f"  {'dataset':<14} {'size':>6}  " + "  ".join(f"{a:>12}" for a in ALGORITHMS)
    print(header)
    print("  " + "-" * (len(header) - 2))

    for ds_name in DATASETS:
        for size in SIZES:
            row = f"  {ds_name:<14} {size:>6}  "
            for algo_name in ALGORITHMS:
                value = results[ds_name][algo_name][size]
                if value is None:
                    row += f"  {'skip':>12}"
                else:
                    row += f"  {value * 1000:>10.2f}ms"
            print(row)
        print()


# ---------- графік ----------

def plot_results(results: dict, filename: str = "benchmark.png") -> None:
    fig, axes = plt.subplots(2, 2, figsize=(12, 9))
    axes = axes.flatten()

    for ax, (ds_name, _) in zip(axes, DATASETS.items()):
        for algo_name in ALGORITHMS:
            # фільтруємо точки де результат None (skipped)
            pairs = [(s, results[ds_name][algo_name][s]) for s in SIZES]
            pairs = [(s, v) for s, v in pairs if v is not None]
            xs = [s for s, _ in pairs]
            ys = [v * 1000 for _, v in pairs]
            ax.plot(xs, ys, marker="o", label=algo_name)

        ax.set_title(f"dataset: {ds_name}")
        ax.set_xlabel("n (розмір)")
        ax.set_ylabel("час, мс")
        ax.set_yscale("log")
        ax.set_xscale("log")
        ax.grid(True, which="both", alpha=0.3)
        ax.legend()

    fig.suptitle("Порівняння сортувань (log-log)", fontsize=14)
    fig.tight_layout()
    fig.savefig(filename, dpi=120)
    print(f"графік збережено: {filename}")


if __name__ == "__main__":
    print("Бенчмарк сортувань. Це займе ~хвилину...")
    results = run_benchmark()
    print_table(results)
    plot_results(results)
