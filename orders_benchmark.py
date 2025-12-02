import time
import cProfile
import random
import timeit
import pstats
from orders import OrderManager,Order

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
        _ = om.Get(idx)
        for order in om:
            om.TryOrder("simu", order)
        if idx > 15:
            om.RemoveOrderAtPriority(random.randint(0,14))
        idx += 1


    bench("Mix (Add + Try + Remove)", op)


def timeit_simu():
    oms = [None for i in range(200)]
    for i in range(200):
        oms[i] =  OrderManager()
        for j in range(3):
            oms[i].Add(DummyOrder(i), j)

    for _ in range(30000): # nb de tours
        for i in range(len(oms)):
            for order in oms[i]:
                order = oms[i].TryOrder("simu", order)


def bench_simu():
    oms = [None for i in range(200)]
    for i in range(200):
        oms[i] =  OrderManager()
        for j in range(3):
            oms[i].Add(DummyOrder(i), j)

    idx = 0

    def op():
        nonlocal idx
        for i in range(len(oms)):
            for order in oms[i]:
                order = oms[i].TryOrder("simu", order)
                #if 1 == random.randint(0, 4):
                #    oms[i].Remove(order)

                #if 1 == random.randint(0, 4):
                #    oms[i].AddMaxPriority(DummyOrder(i))



    bench("Simu 10 orders per troups(200)", op)

if __name__ == "__main__":
    pass
    bench_add()
    bench_get()
    bench_try()
    bench_remove()
    bench_mix()

    #custom
    bench_simu()

    #timeit
    execution_time = timeit.timeit(timeit_simu, number=10000)
    print(f"Execution time: {execution_time:.6f} seconds")

    #cprofile
    cProfile.run('timeit_simu()',"order_impl_stats")
    p = pstats.Stats("order_impl_stats")
    p.sort_stats("cumulative").print_stats()
    p.print_stats()

