import pytest

from Core_Domains.Warehouse.services import WarehouseService            # :contentReference[oaicite:1]{index=1}
from Core_Domains.Warehouse.models import StockItem, InventoryCheckSession
from Core_Domains.Warehouse.value_objects import Quantity, MovementType
from Core_Domains.Warehouse.exceptions import (
    CellNotFound,
    StockItemNotFound,
    NotEnoughStock,
    InventorySessionNotFound,
)

# ================================================================
#   MOCK REPOS (точно соответствуют интерфейсу)
# ================================================================

class CellRepoMock:
    def __init__(self):
        self.data = {}

    def get(self, id):
        if id not in self.data:
            raise KeyError
        return self.data[id]

    def save(self, obj):
        self.data[obj.id] = obj

    def list(self):
        return list(self.data.values())


class StockRepoMock:
    def __init__(self):
        self.data = {}  # (book_id, cell_id) → StockItem

    def get(self, book_id, cell_id):
        if (book_id, cell_id) not in self.data:
            raise KeyError
        return self.data[(book_id, cell_id)]

    def save(self, item):
        self.data[(item.book_id, item.cell_id)] = item

    def delete(self, book_id, cell_id):
        self.data.pop((book_id, cell_id), None)

    def list_by_book(self, book_id):
        return [s for s in self.data.values() if s.book_id == book_id]

    def list_all(self):
        return list(self.data.values())


class MovementRepoMock:
    def __init__(self):
        self.data = []

    def save(self, m):
        self.data.append(m)

    def list_for_book(self, book_id):
        return [m for m in self.data if m.book_id == book_id]


class InventoryRepoMock:
    def __init__(self):
        self.data = {}

    def get(self, id):
        if id not in self.data:
            raise KeyError
        return self.data[id]

    def save(self, session):
        self.data[session.id] = session

    def list(self):
        return list(self.data.values())


# ================================================================
#                         FIXTURE
# ================================================================

@pytest.fixture
def wh():
    return WarehouseService(CellRepoMock(), StockRepoMock(), MovementRepoMock(), InventoryRepoMock())


# ================================================================
#                     INBOUND / OUTBOUND
# ================================================================

def test_inbound_creates_new_stock(wh):
    wh.cell_repo.save(type("Cell", (), {"id": 1}))
    wh.inbound(book_id=10, cell_id=1, qty=5)

    s = wh.stock_repo.get(10, 1)
    assert s.quantity.amount == 5


def test_inbound_adds_to_existing(wh):
    wh.cell_repo.save(type("Cell", (), {"id": 1}))
    wh.inbound(10, 1, 3)
    wh.inbound(10, 1, 2)
    assert wh.stock_repo.get(10, 1).quantity.amount == 5


def test_outbound_ok(wh):
    wh.cell_repo.save(type("Cell", (), {"id": 1}))
    wh.inbound(10, 1, 5)
    wh.outbound(10, 1, 3)

    assert wh.stock_repo.get(10, 1).quantity.amount == 2


def test_outbound_not_enough(wh):
    wh.cell_repo.save(type("Cell", (), {"id": 1}))
    wh.inbound(10, 1, 1)
    with pytest.raises(NotEnoughStock):
        wh.outbound(10, 1, 5)


def test_outbound_stock_missing(wh):
    wh.cell_repo.save(type("Cell", (), {"id": 1}))
    with pytest.raises(StockItemNotFound):
        wh.outbound(10, 1, 1)


# ================================================================
#                           RELOCATE
# ================================================================

def test_relocate_ok(wh):
    wh.cell_repo.save(type("Cell", (), {"id": 1}))
    wh.cell_repo.save(type("Cell", (), {"id": 2}))

    wh.inbound(10, 1, 5)
    wh.relocate(10, 1, 2, 3)

    assert wh.stock_repo.get(10, 1).quantity.amount == 2
    assert wh.stock_repo.get(10, 2).quantity.amount == 3


def test_relocate_stock_missing(wh):
    wh.cell_repo.save(type("Cell", (), {"id": 1}))
    wh.cell_repo.save(type("Cell", (), {"id": 2}))

    with pytest.raises(StockItemNotFound):
        wh.relocate(10, 1, 2, 1)


def test_relocate_not_enough(wh):
    wh.cell_repo.save(type("Cell", (), {"id": 1}))
    wh.cell_repo.save(type("Cell", (), {"id": 2}))

    wh.inbound(10, 1, 2)
    with pytest.raises(NotEnoughStock):
        wh.relocate(10, 1, 2, 5)


def test_relocate_creates_new_target_cell_stock(wh):
    wh.cell_repo.save(type("Cell", (), {"id": 1}))
    wh.cell_repo.save(type("Cell", (), {"id": 2}))
    wh.inbound(10, 1, 5)

    wh.relocate(10, 1, 2, 1)
    assert wh.stock_repo.get(10, 2).quantity.amount == 1


# ================================================================
#                        MOVEMENT LOG
# ================================================================

def test_movement_log_records(wh):
    wh.cell_repo.save(type("Cell", (), {"id": 1}))
    wh.inbound(10, 1, 3)
    m = wh.movement_repo.list_for_book(10)

    assert len(m) == 1
    assert m[0].movement_type == MovementType.INBOUND


def test_relocation_log(wh):
    wh.cell_repo.save(type("Cell", (), {"id": 1}))
    wh.cell_repo.save(type("Cell", (), {"id": 2}))
    wh.inbound(10, 1, 10)
    wh.relocate(10, 1, 2, 5)

    m = wh.movement_repo.list_for_book(10)
    assert m[-1].movement_type == MovementType.RELOCATION


# ================================================================
#                      INVENTORY SESSION
# ================================================================

def test_start_inventory_session(wh):
    s = wh.start_inventory_session()
    assert isinstance(s, InventoryCheckSession)
    assert s.id is not None


def test_inventory_add_result_existing_stock(wh):
    # Add cell & stock
    wh.cell_repo.save(type("Cell", (), {"id": 1}))
    wh.inbound(10, 1, 5)

    session = wh.start_inventory_session()
    wh.add_inventory_result(session.id, 10, 1, actual_qty=3)

    s2 = wh.inventory_repo.get(session.id)
    assert len(s2.items) == 1
    assert s2.items[0].expected_qty == 5
    assert s2.items[0].actual_qty == 3


def test_inventory_add_result_no_stock(wh):
    wh.cell_repo.save(type("Cell", (), {"id": 1}))

    session = wh.start_inventory_session()
    wh.add_inventory_result(session.id, 99, 1, actual_qty=4)

    s2 = wh.inventory_repo.get(session.id)
    assert s2.items[0].expected_qty == 0
    assert s2.items[0].actual_qty == 4


def test_close_inventory_and_apply_positive_diff(wh):
    wh.cell_repo.save(type("Cell", (), {"id": 1}))
    wh.inbound(10, 1, 5)

    session = wh.start_inventory_session()
    wh.add_inventory_result(session.id, 10, 1, actual_qty=8)

    wh.close_inventory_and_apply(session.id)

    assert wh.stock_repo.get(10, 1).quantity.amount == 8


def test_close_inventory_and_apply_negative_diff(wh):
    wh.cell_repo.save(type("Cell", (), {"id": 1}))
    wh.inbound(10, 1, 10)

    session = wh.start_inventory_session()
    wh.add_inventory_result(session.id, 10, 1, actual_qty=4)

    wh.close_inventory_and_apply(session.id)

    assert wh.stock_repo.get(10, 1).quantity.amount == 4


def test_inventory_not_found(wh):
    with pytest.raises(InventorySessionNotFound):
        wh.close_inventory_and_apply(123456)
