# -*- coding: utf-8 -*-
"""
Лабораторная работа № 3. Вариант 12.
Файл: lab3.py

Параметры варианта 12:
    Опорный элемент: Сл (Случайный)
    Разбиение: Х (Схема Хоара)
    Слияние: Н (Нисходящее рекурсивное)
    Размеры n (Эксперимент 2): 20000, 40000, 80000, 160000
    Доп. задание: Г6 (Трёхпутевое разбиение Дейкстры)
"""

import random
import time
import statistics
import csv
import matplotlib.pyplot as plt

# Импортируем сортировки из ЛР № 2 (lab2.py)
try:
    from lab2 import bubble_sort, insertion_sort
except ImportError:
    print("Ошибка: Убедитесь, что файл lab2.py находится в той же папке.")
    exit(1)


# ----------------------------------------------------------------------
# Генератор данных (локальный для ЛР3, поддерживает все типы)
# ----------------------------------------------------------------------
def generate_data(n, kind="random", lo=-10_000, hi=10_000, seed=42):
    """Генерирует массив длины n заданного типа."""
    rng = random.Random(seed + n)

    if kind == "duplicates":
        # Узкий диапазон для большого числа повторов
        data = [rng.randint(0, 10) for _ in range(n)]
    else:
        data = [rng.randint(lo, hi) for _ in range(n)]
        if kind == "sorted":
            data.sort()
        elif kind == "reversed":
            data.sort(reverse=True)
        elif kind == "nearly_sorted":
            data.sort()
            for _ in range(max(1, n // 20)):  # 5% перестановок
                i, j = rng.randrange(n), rng.randrange(n)
                data[i], data[j] = data[j], data[i]

    return data


# ----------------------------------------------------------------------
# 1. Сортировка слиянием (нисходящая рекурсивная)
# ----------------------------------------------------------------------
def merge_sort(arr):
    if len(arr) <= 1:
        return arr.copy()
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return _merge(left, right)


def _merge(left, right):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:  # <= обеспечивает устойчивость
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result


# ----------------------------------------------------------------------
# 2. Быстрая сортировка (Опорный: Случайный, Разбиение: Хоара)
# ----------------------------------------------------------------------
def quick_sort(arr):
    a = arr.copy()
    _quick_sort(a, 0, len(a) - 1)
    return a


def _quick_sort(a, lo, hi):
    while lo < hi:
        p = _partition_hoare(a, lo, hi)
        # Рекурсия в меньшую часть для ограничения глубины стека O(log n)
        if p - lo < hi - p:
            _quick_sort(a, lo, p)
            lo = p + 1
        else:
            _quick_sort(a, p + 1, hi)
            hi = p


def _partition_hoare(a, lo, hi):
    # Случайный выбор опорного элемента
    pivot_idx = random.randint(lo, hi)
    pivot = a[pivot_idx]

    i, j = lo - 1, hi + 1
    while True:
        i += 1
        while a[i] < pivot:
            i += 1
        j -= 1
        while a[j] > pivot:
            j -= 1
        if i >= j:
            return j
        a[i], a[j] = a[j], a[i]


# ----------------------------------------------------------------------
# 3. Дополнительное задание Г6: Трёхпутевое разбиение (Голландский флаг)
# ----------------------------------------------------------------------
def quick_sort_3way(arr):
    a = arr.copy()
    _quick_sort_3way(a, 0, len(a) - 1)
    return a


def _quick_sort_3way(a, lo, hi):
    while lo < hi:
        lt, gt = _partition_3way(a, lo, hi)
        # Рекурсивно обрабатываем меньшую часть
        if lt - lo < hi - gt:
            _quick_sort_3way(a, lo, lt - 1)
            lo = gt + 1
        else:
            _quick_sort_3way(a, gt + 1, hi)
            hi = lt - 1


def _partition_3way(a, lo, hi):
    pivot = a[lo]
    lt = lo
    gt = hi
    i = lo
    while i <= gt:
        if a[i] < pivot:
            a[lt], a[i] = a[i], a[lt]
            lt += 1
            i += 1
        elif a[i] > pivot:
            a[gt], a[i] = a[i], a[gt]
            gt -= 1
        else:
            i += 1
    return lt, gt


# ----------------------------------------------------------------------
# Замер времени
# ----------------------------------------------------------------------
def measure(sort_func, data, repeats=3):
    times = []
    for _ in range(repeats):
        start = time.perf_counter()
        result = sort_func(data)
        times.append(time.perf_counter() - start)
        # Проверка корректности
        assert result == sorted(data), f"{sort_func.__name__} работает некорректно!"
    return statistics.median(times)


# ----------------------------------------------------------------------
# Эксперименты
# ----------------------------------------------------------------------
def run_experiments():
    print("=" * 70)
    print("Лабораторная работа № 3. Вариант 12 (файл lab3.py)")
    print("=" * 70)

    # --- Эксперимент 1: Сравнение 4 алгоритмов (размеры из ЛР2 для Вар.12) ---
    sizes1 = [500, 1000, 2000, 3000, 4000]
    algos1 = {"Bubble": bubble_sort, "Insertion": insertion_sort,
              "Quick": quick_sort, "Merge": merge_sort}
    res1 = {name: [] for name in algos1}

    print("\nЭксперимент 1: Квадратичные vs O(n log n)")
    print(f"{'n':>6} | {'Bubble':>10} | {'Insertion':>10} | {'Quick':>10} | {'Merge':>10}")
    print("-" * 60)
    for n in sizes1:
        data = generate_data(n)
        row = f"{n:>6} |"
        for name, func in algos1.items():
            t = measure(func, data)
            res1[name].append(t)
            row += f" {t:>10.4f} |"
        print(row)

    with open("lab3_exp1.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["n", "bubble", "insertion", "quick", "merge"])
        for i, n in enumerate(sizes1):
            w.writerow([n, res1["Bubble"][i], res1["Insertion"][i], res1["Quick"][i], res1["Merge"][i]])

    # --- Эксперимент 2: O(n log n) на больших массивах ---
    sizes2 = [20000, 40000, 80000, 160000]
    algos2 = {"Quick": quick_sort, "Merge": merge_sort, "sorted": sorted}
    res2 = {name: [] for name in algos2}

    print(f"\nЭксперимент 2: Большие массивы (n = {sizes2})")
    print(f"{'n':>6} | {'Quick':>10} | {'Merge':>10} | {'sorted()':>10}")
    print("-" * 48)
    for n in sizes2:
        data = generate_data(n)
        row = f"{n:>6} |"
        for name, func in algos2.items():
            t = measure(func, data, repeats=1)  # 1 повтор для скорости на больших n
            res2[name].append(t)
            row += f" {t:>10.4f} |"
        print(row)

    with open("lab3_exp2.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["n", "quick", "merge", "sorted"])
        for i, n in enumerate(sizes2):
            w.writerow([n, res2["Quick"][i], res2["Merge"][i], res2["sorted"][i]])

    # --- Эксперимент 3: Влияние структуры данных (n = 50000) ---
    n3 = 50000
    kinds = ["random", "sorted", "reversed", "nearly_sorted", "duplicates"]
    print(f"\nЭксперимент 3: Влияние структуры данных (n = {n3})")
    print(f"{'Тип данных':>15} | {'Quick (Сл, Х)':>15} | {'Merge':>10}")
    print("-" * 48)
    res3_quick = []
    res3_merge = []
    for kind in kinds:
        data = generate_data(n3, kind=kind)
        t_q = measure(quick_sort, data, repeats=1)
        t_m = measure(merge_sort, data, repeats=1)
        res3_quick.append(t_q)
        res3_merge.append(t_m)
        print(f"{kind:>15} | {t_q:>15.4f} | {t_m:>10.4f}")

    # --- Эксперимент 4 (Г6): Трёхпутевое разбиение vs Классическое на дубликатах ---
    print(f"\nЗадание Г6: Сравнение на дубликатах (n = {n3}, тип D)")
    data_d = generate_data(n3, kind="duplicates")
    t_classic = measure(quick_sort, data_d, repeats=1)
    t_3way = measure(quick_sort_3way, data_d, repeats=1)
    print(f"Классическая быстрая (Хоар): {t_classic:.4f} с")
    print(f"Трёхпутевая (Дейкстра):      {t_3way:.4f} с")

    with open("lab3_exp4.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["algorithm", "time"])
        w.writerow(["classic_quick", t_classic])
        w.writerow(["3way_quick", t_3way])

    # --- Построение графиков ---
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # График 1: Эксперимент 1
    for name, t in res1.items():
        axes[0].plot(sizes1, t, marker="o", label=name)
    axes[0].set_yscale("log")
    axes[0].set_title("Эксперимент 1: Все 4 алгоритма (лог. шкала)")
    axes[0].set_xlabel("Размер массива n")
    axes[0].set_ylabel("Время, с")
    axes[0].grid(True, which="both", linestyle="--", alpha=0.7)
    axes[0].legend()

    # График 2: Эксперимент 2
    for name, t in res2.items():
        axes[1].plot(sizes2, t, marker="o", label=name)
    axes[1].set_title("Эксперимент 2: Быстрая, Слиянием и sorted()")
    axes[1].set_xlabel("Размер массива n")
    axes[1].set_ylabel("Время, с")
    axes[1].grid(True, linestyle="--", alpha=0.7)
    axes[1].legend()

    plt.tight_layout()
    plt.savefig("lab3_plot.png", dpi=150)
    print("\nГрафик сохранен в lab3_plot.png")


if __name__ == "__main__":
    run_experiments()