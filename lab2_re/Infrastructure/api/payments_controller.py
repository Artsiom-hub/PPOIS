# infrastructure/api/payments_controller.py

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from .dependencies import get_payment_service
from Core_Domains.Payments.services import PaymentService
from Core_Domains.Payments.value_objects import Money

router = APIRouter(prefix="/payments", tags=["Payments"])


class TransferDTO(BaseModel):
    from_account: int
    to_account: int
    amount: float


@router.post("/transfer")
def transfer(dto: TransferDTO, svc: PaymentService = Depends(get_payment_service)):
    trx = svc.transfer(dto.from_account, dto.to_account, Money(dto.amount))
    return {"transaction_id": trx.id, "status": trx.status.value}
