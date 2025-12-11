# lab2re/Unit_tests/test_CoreDomains/Test_Warehouse.py

import pytest
from datetime import datetime

from Core_Domains.Warehouse.services import WarehouseService
from Core_Domains.Warehouse.models import (
    Cell, StockItem, InventoryCheckSession
)
from Core_Domains.Warehouse.value_objects import Quantity, MovementType
from Core_Domains.Warehouse.exceptions import (
    CellNotFound, StockItemNotFound, NotEnoughStock,
    InventorySessionNotFound
)

from Core_Domains.Warehouse.repository_interface import (
    CellRepository, StockRepository, StockMovementRepository, InventorySessionRepository
)


# ============================================================
#                 In-memory repositories
# ============================================================

class CellRepo(CellRepository):
    def __init__(self):
        self.cells = {}

    def get(self, cell_id: int) -> Cell:
        if cell_id not in self.cells:
            raise KeyError(cell_id)
        return self.cells[cell_id]

    def list_by_shelf(self, shelf_id: int):
        return [c for c in self.cells.values() if c.shelf_id == shelf_id]

    def save(self, cell: Cell):
        self.cells[cell.id] = cell


class StockRepo(StockRepository):
    def __init__(self):
        self.stock = {}  # (book_id, cell_id) → StockItem

    def get(self, book_id: int, cell_id: int) -> StockItem:
        key = (book_id, cell_id)
        if key not in self.stock:
            raise KeyError(key)
        return self.stock[key]

    def list_by_book(self, book_id: int):
        return [s for (b, _), s in self.stock.items() if b == book_id]

    def list_by_cell(self, cell_id: int):
        return [s for (_, c), s in self.stock.items() if c == cell_id]

    def save(self, stock_item: StockItem):
        self.stock[(stock_item.book_id, stock_item.cell_id)] = stock_item

    def delete(self, book_id: int, cell_id: int):
        key = (book_id, cell_id)
        if key in self.stock:
            del self.stock[key]

    def list_all(self):
        return list(self.stock.values())


class MovementRepo(StockMovementRepository):
    def __init__(self):
        self.movements = []

    def save(self, movement):
        self.movements.append(movement)

    def list_for_book(self, book_id: int):
        return [m for m in self.movements if m.book_id == book_id]


class InventoryRepo(InventorySessionRepository):
    def __init__(self):
        self.sessions = {}

    def get(self, session_id: int) -> InventoryCheckSession:
        if session_id not in self.sessions:
            raise KeyError(session_id)
        return self.sessions[session_id]

    def save(self, session: InventoryCheckSession):
        self.sessions[session.id] = session

    def list(self):
        return list(self.sessions.values())


# ============================================================
#                       Fixtures
# ============================================================

@pytest.fixture
def cell_repo():
    return CellRepo()

@pytest.fixture
def stock_repo():
    return StockRepo()

@pytest.fixture
def movement_repo():
    return MovementRepo()

@pytest.fixture
def inventory_repo():
    return InventoryRepo()

@pytest.fixture
def service(cell_repo, stock_repo, movement_repo, inventory_repo):
    return WarehouseService(cell_repo, stock_repo, movement_repo, inventory_repo)


@pytest.fixture
def sample_cell():
    return Cell(id=10, shelf_id=1, code="A-01-10", capacity=500)


# ============================================================
#                           TESTS
# ============================================================

# ---------- inbound ----------

def test_inbound_creates_new_stock(service, cell_repo, stock_repo, sample_cell):
    cell_repo.save(sample_cell)

    service.inbound(book_id=1, cell_id=10, qty=5)

    stock = stock_repo.get(1, 10)
    assert stock.quantity.amount == 5
    assert len(stock_repo.list_all()) == 1


def test_inbound_invalid_cell(service):
    with pytest.raises(CellNotFound):
        service.inbound(book_id=1, cell_id=999, qty=5)


# ---------- outbound ----------

def test_outbound_success(service, cell_repo, stock_repo, sample_cell):
    cell_repo.save(sample_cell)

    stock_repo.save(StockItem(book_id=1, cell_id=10, quantity=Quantity(10)))

    service.outbound(1, 10, 4)

    assert stock_repo.get(1, 10).quantity.amount == 6


def test_outbound_stock_not_found(service, cell_repo, sample_cell):
    cell_repo.save(sample_cell)

    with pytest.raises(StockItemNotFound):
        service.outbound(1, 10, 5)


def test_outbound_not_enough_stock(service, cell_repo, stock_repo, sample_cell):
    cell_repo.save(sample_cell)
    stock_repo.save(StockItem(book_id=1, cell_id=10, quantity=Quantity(2)))

    with pytest.raises(NotEnoughStock):
        service.outbound(1, 10, 5)


def test_outbound_zero_deletes_stock(service, cell_repo, stock_repo, sample_cell):
    cell_repo.save(sample_cell)
    stock_repo.save(StockItem(book_id=1, cell_id=10, quantity=Quantity(3)))

    service.outbound(1, 10, 3)

    assert stock_repo.list_all() == []


# ---------- relocate ----------

def test_relocate_success(service, cell_repo, stock_repo):
    c1 = Cell(id=1, shelf_id=1, code="A-1", capacity=100)
    c2 = Cell(id=2, shelf_id=1, code="A-2", capacity=100)
    cell_repo.save(c1)
    cell_repo.save(c2)

    stock_repo.save(StockItem(book_id=1, cell_id=1, quantity=Quantity(10)))

    service.relocate(book_id=1, from_cell_id=1, to_cell_id=2, qty=4)

    assert stock_repo.get(1, 1).quantity.amount == 6
    assert stock_repo.get(1, 2).quantity.amount == 4


def test_relocate_not_enough_stock(service, cell_repo, stock_repo):
    c1 = Cell(id=1, shelf_id=1, code="A-1", capacity=100)
    c2 = Cell(id=2, shelf_id=1, code="A-2", capacity=100)
    cell_repo.save(c1); cell_repo.save(c2)

    stock_repo.save(StockItem(book_id=1, cell_id=1, quantity=Quantity(3)))

    with pytest.raises(NotEnoughStock):
        service.relocate(1, 1, 2, 10)


def test_relocate_missing_cell(service, cell_repo, stock_repo):
    c1 = Cell(id=1, shelf_id=1, code="A-1", capacity=100)
    cell_repo.save(c1)

    stock_repo.save(StockItem(book_id=1, cell_id=1, quantity=Quantity(3)))

    with pytest.raises(CellNotFound):
        service.relocate(1, 1, 999, 1)


# ---------- total stock ----------

def test_total_stock(service, cell_repo, stock_repo):
    cell_repo.save(Cell(id=1, shelf_id=1, code="A", capacity=100))
    cell_repo.save(Cell(id=2, shelf_id=1, code="B", capacity=100))

    stock_repo.save(StockItem(book_id=5, cell_id=1, quantity=Quantity(3)))
    stock_repo.save(StockItem(book_id=5, cell_id=2, quantity=Quantity(7)))

    total = service.get_total_stock_for_book(5)
    assert total == 10


# ---------- inventory session ----------

def test_start_inventory_session(service, inventory_repo):
    session = service.start_inventory_session()
    assert session.id in inventory_repo.sessions


def test_add_inventory_result_creates_items(service, cell_repo, stock_repo, inventory_repo):
    cell_repo.save(Cell(id=10, shelf_id=1, code="C-10", capacity=100))
    stock_repo.save(StockItem(book_id=1, cell_id=10, quantity=Quantity(5)))

    session = service.start_inventory_session()

    service.add_inventory_result(
        session_id=session.id,
        book_id=1,
        cell_id=10,
        actual_qty=3
    )

    saved = inventory_repo.get(session.id)
    assert len(saved.items) == 1
    assert saved.items[0].expected_qty == 5
    assert saved.items[0].actual_qty == 3


def test_add_inventory_result_no_stock_expected_zero(service, cell_repo, inventory_repo):
    cell_repo.save(Cell(id=10, shelf_id=1, code="C-10", capacity=100))

    session = service.start_inventory_session()

    service.add_inventory_result(session.id, 99, 10, actual_qty=7)

    saved = inventory_repo.get(session.id)
    assert saved.items[0].expected_qty == 0
    assert saved.items[0].actual_qty == 7


def test_add_inventory_result_session_not_found(service):
    with pytest.raises(InventorySessionNotFound):
        service.add_inventory_result(999999, 1, 1, 5)


# ---------- close & apply ----------

def test_inventory_apply_adjusts_stock(service, cell_repo, stock_repo, inventory_repo):
    # base stock
    cell_repo.save(Cell(id=10, shelf_id=1, code="C-10", capacity=100))
    stock_repo.save(StockItem(book_id=1, cell_id=10, quantity=Quantity(5)))

    session = service.start_inventory_session()

    # actual < expected → outbound
    service.add_inventory_result(session.id, 1, 10, actual_qty=2)

    # actual > expected → inbound (2 rows)
    service.add_inventory_result(session.id, 2, 10, actual_qty=3)

    service.close_inventory_and_apply(session.id)

    # book 1: 5 → 2
    assert stock_repo.get(1, 10).quantity.amount == 2

    # book 2: 0 → 3
    assert stock_repo.get(2, 10).quantity.amount == 3
