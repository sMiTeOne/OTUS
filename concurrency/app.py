import time
from threading import (
    Lock,
    Thread,
)


lock = Lock()

def print_nums_1() -> None:
    """Вывод чисел от 1 до 10"""
    for i in range(1, 11):
        time.sleep(0.1)
        print(i)

def print_nums_2() -> None:
    """Вывод чисел от 1 до 10 с блокировкой"""
    with lock:
        print_nums_1()

def build_threads_1() -> list[Thread]:
    """Возвращает список потоков"""
    return [Thread(target=print_nums_1) for _ in range(5)]

def build_threads_2() -> list[Thread]:
    """Возвращает список потоков с блокировкой"""
    return [Thread(target=print_nums_2) for _ in range(5)]

def run_threads(threads: list[Thread]) -> None:
    """Запуск потоков"""
    for thread in threads:
        thread.start()

def wait_threads(threads: list[Thread]) -> None:
    """Ожидание завершения выполнения потоков"""
    for thread in threads:
        thread.join()
    print('Все потоки успешно выполнились!')

# Запуск потоков, работающих одновременно
threads = build_threads_1()
run_threads(threads)
wait_threads(threads)

# Запуск потоков, работающих синхронно
threads = build_threads_2()
run_threads(threads)
wait_threads(threads)
