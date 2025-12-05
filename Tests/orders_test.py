import pytest
from Model.orders import OrderManager


class DummyOrder:
    def __init__(self, name):
        self.name = name


def test_add_and_get():
    om = OrderManager()
    o1 = DummyOrder("A")
    o2 = DummyOrder("B")

    om.Add(o1, 0)
    om.Add(o2, 1)

    assert om.Get(0) is o1
    assert om.Get(1) is o2
    assert om.Get(2) is None

def test_add_with_max_priority():
    om = OrderManager()
    o1 = DummyOrder("A")
    o2 = DummyOrder("B")
    o3 = DummyOrder("C")

    om.Add(o1, 0)
    om.AddMaxPriority(o2) # Should be priority 1
    om.AddMaxPriority(o3) # Should be priority 2

    assert om.Get(0) is o1
    assert om.Get(1) is o2
    assert om.Get(2) is o3

    om_empty = OrderManager()
    o4 = DummyOrder("D")
    om_empty.AddWithMaxPriority(o4) # Should be priority 0
    assert om_empty.Get(0) is o4

def test_add_priority_conflict():
    om = OrderManager()
    o = DummyOrder("X")
    om.Add(o, 0)
    with pytest.raises(ValueError):
        om.Add(DummyOrder("Y"), 0)


def test_remove_by_order():
    om = OrderManager()
    o1 = DummyOrder("A")
    o2 = DummyOrder("B")

    om.Add(o1, 0)
    om.Add(o2, 1)

    assert om.Remove(o1) is True
    assert om.Get(0) is None
    assert len(om) == 1

    assert om.Remove(o1) is False


def test_remove_by_priority():
    om = OrderManager()
    o1 = DummyOrder("A")
    o2 = DummyOrder("B")

    om.Add(o1, 0)
    om.Add(o2, 1)

    assert om.RemoveOrderAtPriority(0) is True
    assert om.Get(0) is None
    assert len(om) == 1

    assert om.RemoveOrderAtPriority(5) is False


def test_iteration_order():
    om = OrderManager()
    o1 = DummyOrder("A")
    o2 = DummyOrder("B")
    o3 = DummyOrder("C")

    om.Add(o1, 0)
    om.Add(o2, 2)
    om.Add(o3, 1)

    res = list(om)
    assert res == [o1, o3, o2]


def test_remove_during_iteration():
    om = OrderManager()
    o1 = DummyOrder("A")
    o2 = DummyOrder("B")
    o3 = DummyOrder("C")

    om.Add(o1, 0)
    om.Add(o2, 1)
    om.Add(o3, 2)

    seen = []
    for o in list(om):
        seen.append(o)
        om.Remove(o)

    assert seen == [o1, o2, o3]
    assert len(om) == 0