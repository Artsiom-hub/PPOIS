class OrderProcessingError(Exception):
    pass


class OrderNotFound(OrderProcessingError):
    def __init__(self, order_id: int):
        super().__init__(f"Order with id={order_id} not found")


class InvalidOrderOperation(OrderProcessingError):
    pass
