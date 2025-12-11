# infrastructure/api/warehouse_controller.py

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from .dependencies import get_warehouse_service
from Core_Domains.Warehouse.services import WarehouseService

router = APIRouter(prefix="/warehouse", tags=["Warehouse"])


class InboundDTO(BaseModel):
    book_id: int
    cell_id: int
    qty: int


@router.post("/inbound")
def inbound(dto: InboundDTO, svc: WarehouseService = Depends(get_warehouse_service)):
    svc.inbound(dto.book_id, dto.cell_id, dto.qty)
    return {"status": "ok"}


class RelocateDTO(BaseModel):
    book_id: int
    from_cell: int
    to_cell: int
    qty: int


@router.post("/relocate")
def relocate(dto: RelocateDTO, svc: WarehouseService = Depends(get_warehouse_service)):
    svc.relocate(dto.book_id, dto.from_cell, dto.to_cell, dto.qty)
    return {"status": "ok"}
