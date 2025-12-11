# infrastructure/api/order_controller.py

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from .dependencies import get_order_service
from Core_Domains.Order_Processing.services import OrderService

router = APIRouter(prefix="/orders", tags=["Orders"])


class OrderCreateDTO(BaseModel):
    customer_id: int


class AddBookDTO(BaseModel):
    book_id: int
    qty: int


@router.post("/create")
def create_order(
    dto: OrderCreateDTO,
    svc: OrderService = Depends(get_order_service)
):
    order = svc.create_order(dto.customer_id)
    return {"order_id": order.id}


@router.post("/{order_id}/add-book")
def add_book(order_id: int, dto: AddBookDTO, svc: OrderService = Depends(get_order_service)):
    svc.add_book(order_id, dto.book_id, dto.qty)
    return {"status": "ok"}


@router.post("/{order_id}/pay")
def pay(order_id: int, svc: OrderService = Depends(get_order_service)):
    svc.pay(order_id)
    return {"status": "paid"}
