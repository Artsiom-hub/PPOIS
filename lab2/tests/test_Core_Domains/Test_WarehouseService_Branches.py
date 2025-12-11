import pytest
from datetime import datetime

from Core_Domains.Warehouse.services import WarehouseService          # :contentReference[oaicite:0]{index=0}
from Core_Domains.Warehouse.models import (
    Cell,
    StockItem,
    StockMovement,
    InventoryCheckSession,
)
from Core_Domains.Warehouse.value_objects import (
    Quantity,
    MovementType,
)
from Core_Domains.Warehouse.exceptions import (
    CellNotFound,
    StockItemNotFound,
    NotEnoughStock,
    WarehouseError,
    InventorySessionNotFound,
)


# =====================================================================
#                           MOCK REPOSITORIES
# =====================================================================

class CellRepoMock:
    def __init__(self):
        self.data = {}

    def get(self, id):
        if id not in self.data:
            raise KeyError
        return self.data[id]

    def save(self, cell):
        self.data[cell.id] = cell

    def list(self):
        return list(self.data.values())

    def delete(self, id):
        self.data.pop(id, None)


class StockRepoMock:
    def __init__(self):
        self.data = {}      # (book_id, cell_id) → StockItem

    def get(self, book_id, cell_id):
        key = (book_id, cell_id)
        if key not in self.data:
            raise KeyError
        return self.data[key]

    def save(self, item):
        key = (item.book_id, item.cell_id)
        self.data[key] = item

    def delete(self, book_id, cell_id):
        self.data.pop((book_id, cell_id), None)

    def list_by_cell(self, cell_id):
        return [x for x in self.data.values() if x.cell_id == cell_id]

    def list_by_book(self, book_id):
        return [x for x in self.data.values() if x.book_id == book_id]


class MovementRepoMock:
    def __init__(self):
        self.data = []

    def save(self, mvt):
        self.data.append(mvt)

    def list_for_book(self, book_id):
        return [m for m in self.data if m.book_id == book_id]

    # ✔️ сервис вызывает .list(), поэтому добавляем алиас
    def list(self, book_id):
        return self.list_for_book(book_id)



class InventoryRepoMock:
    def __init__(self):
        self.data = {}

    def get(self, id):
        if id not in self.data:
            raise KeyError
        return self.data[id]

    def save(self, sess):
        self.data[sess.id] = sess

    def list(self):
        return list(self.data.values())


# =====================================================================
#                             FIXTURE
# =====================================================================

@pytest.fixture
def wh():
    return WarehouseService(
        CellRepoMock(),
        StockRepoMock(),
        MovementRepoMock(),
        InventoryRepoMock()
    )


# =====================================================================
#                             CELL TESTS
# =====================================================================

def test_create_cell(wh):
    c = wh.create_cell(1, "A-1", capacity=50)
    assert c.id == 1
    assert c.capacity == 50


def test_list_cells(wh):
    wh.create_cell(1, "A", 10)
    wh.create_cell(2, "B", 20)
    assert len(wh.list_cells()) == 2


def test_get_cell_not_found(wh):
    with pytest.raises(CellNotFound):
        wh.get_cell(999)


# =====================================================================
#                         INBOUND TESTS
# =====================================================================

def test_inbound_new_stock_created(wh):
    wh.create_cell(1, "A", 100)
    wh.inbound(10, 1, 5, "init")
    s = wh.get_stock(10, 1)
    assert s.quantity.amount == 5


def test_inbound_add_to_existing_stock(wh):
    wh.create_cell(1, "A", 100)
    wh.inbound(10, 1, 3, "1st")
    wh.inbound(10, 1, 2, "2nd")
    assert wh.get_stock(10, 1).quantity.amount == 5


def test_inbound_over_capacity(wh):
    wh.create_cell(1, "A", 5)
    wh.inbound(10, 1, 5, "ok")
    with pytest.raises(WarehouseError):
        wh.inbound(10, 1, 1, "overflow")


# =====================================================================
#                         OUTBOUND TESTS
# =====================================================================

def test_outbound_ok(wh):
    wh.create_cell(1, "A", 100)
    wh.inbound(10, 1, 5, "init")
    wh.outbound(10, 1, 3, "ship")
    assert wh.get_stock(10, 1).quantity.amount == 2


def test_outbound_not_enough(wh):
    wh.create_cell(1, "A", 100)
    wh.inbound(10, 1, 2, "init")
    with pytest.raises(NotEnoughStock):
        wh.outbound(10, 1, 5, "nope")


def test_outbound_stock_not_found(wh):
    wh.create_cell(1, "A", 100)
    with pytest.raises(StockItemNotFound):
        wh.outbound(10, 1, 1, "out")


# =====================================================================
#                         MOVE TESTS
# =====================================================================

def test_move_simple(wh):
    wh.create_cell(1, "A", 100)
    wh.create_cell(2, "B", 100)

    wh.inbound(10, 1, 5, "init")
    wh.move(10, 1, 2, 3, "move")

    assert wh.get_stock(10, 1).quantity.amount == 2
    assert wh.get_stock(10, 2).quantity.amount == 3


def test_move_same_cell(wh):
    wh.create_cell(1, "A", 100)
    wh.inbound(10, 1, 5, "init")
    with pytest.raises(NotEnoughStock):
        wh.move(10, 1, 1, 2, "same")


def test_move_not_enough(wh):
    wh.create_cell(1, "A", 100)
    wh.create_cell(2, "B", 100)

    wh.inbound(10, 1, 2, "init")
    with pytest.raises(NotEnoughStock):
        wh.move(10, 1, 2, 5, "nope")


def test_move_over_capacity(wh):
    wh.create_cell(1, "A", 100)
    wh.create_cell(2, "B", 2)

    wh.inbound(10, 1, 5, "init")
    wh.inbound(10, 2, 2, "init2")

    with pytest.raises(WarehouseError):
        wh.move(10, 1, 2, 3, "overflow")


def test_move_creates_new_stock(wh):
    wh.create_cell(1, "A", 100)
    wh.create_cell(2, "B", 100)

    wh.inbound(10, 1, 5, "init")
    wh.move(10, 1, 2, 1, "move")

    assert wh.get_stock(10, 2).quantity.amount == 1


def test_move_stock_missing(wh):
    wh.create_cell(1, "A", 100)
    wh.create_cell(2, "B", 100)

    with pytest.raises(StockItemNotFound):
        wh.move(10, 1, 2, 3, "missing")


# =====================================================================
#                       MOVEMENT LOG TESTS
# =====================================================================

def test_movement_log_inbound(wh):
    wh.create_cell(1, "A", 100)
    wh.inbound(10, 1, 5, "init")
    lst = wh.list_movements(10)
    assert len(lst) == 1
    assert lst[0].movement_type == MovementType.INBOUND


def test_movement_log_outbound(wh):
    wh.create_cell(1, "A", 100)
    wh.inbound(10, 1, 10, "init")
    wh.outbound(10, 1, 3, "ship")
    lst = wh.list_movements(10)
    assert lst[-1].movement_type == MovementType.OUTBOUND


def test_movement_log_move(wh):
    wh.create_cell(1, "A", 100)
    wh.create_cell(2, "B", 100)

    wh.inbound(10, 1, 20, "init")
    wh.move(10, 1, 2, 5, "move")

    lst = wh.list_movements(10)
    assert lst[-1].movement_type == MovementType.MOVE


# =====================================================================
#                       INVENTORY TESTS
# =====================================================================

def test_inventory_start(wh):
    s = wh.start_inventory(1)
    assert s.id == 1
    assert s.started_at is not None


def test_inventory_add_result(wh):
    s = wh.start_inventory(1)
    wh.add_inventory_result(
        session_id=1,
        book_id=10,
        cell_id=1,
        expected=5,
        actual=4,
    )
    assert len(s.items) == 1
    assert s.items[0].actual_qty == 4


def test_inventory_finish(wh):
    s = wh.start_inventory(1)
    wh.finish_inventory(1)
    assert s.finished_at is not None


def test_inventory_get(wh):
    wh.start_inventory(1)
    s = wh.get_inventory(1)
    assert s.id == 1


def test_inventory_get_not_found(wh):
    with pytest.raises(InventorySessionNotFound):
        wh.get_inventory(999)


def test_inventory_list(wh):
    wh.start_inventory(1)
    wh.start_inventory(2)
    lst = wh.list_inventory()
    assert len(lst) == 2
