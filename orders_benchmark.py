import time
from orders import OrderManager

NORDER = 5000
NTIME = 1.0

class DummyOrder:
    def __init__(self, x):
        self.x = x
    def Try(self, simu):
        return


def bench(label, func):
    start = time.perf_counter()
    count = 0
    end_time = start + NTIME   # on mesure sur 1 seconde

    while time.perf_counter() < end_time:
        func()
        count += 1

    duration = time.perf_counter() - start
    print(f"{label}: {count} opérations en {duration:.3f}s => {int(count/duration)} ops/sec")


def bench_add():
    om = OrderManager()
    i = 0

    def op():
        nonlocal i
        om.Add(DummyOrder(i), i)
        i += 1

    bench("Add", op)


def bench_get():
    om = OrderManager()
    for i in range(NORDER):
        om.Add(DummyOrder(i), i)

    i = 0

    def op():
        nonlocal i
        om.Get(i % NORDER)
        i += 1

    bench("Get", op)

def bench_try():
    om = OrderManager()
    for i in range(NORDER):
        om.Add(DummyOrder(i), i)

    i = 0

    def op():
        nonlocal i
        order = om.Get(i % NORDER)
        om.TryOrder("simu", order)
        i += 1

    bench("try", op)

def bench_remove():
    om = OrderManager()
    for i in range(2000):
        om.Add(DummyOrder(i), i)

    i = 0

    def op():
        nonlocal i
        om.RemoveOrderAtPriority(i % NORDER)
        i += 1

    bench("Remove", op)


def bench_mix():
    om = OrderManager()
    idx = 0

    def op():
        nonlocal idx
        om.Add(DummyOrder(idx), idx)
        order = om.Get(idx)
        om.TryOrder("simu", order)
        if idx > 0:
            om.RemoveOrderAtPriority(idx - 1)
        idx += 1


    bench("Mix (Add + Try + Remove)", op)


if __name__ == "__main__":
    bench_add()
    bench_get()
    bench_try()
    bench_remove()
    bench_mix()
