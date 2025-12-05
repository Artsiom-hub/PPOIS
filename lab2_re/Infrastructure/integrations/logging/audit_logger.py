import logging

audit_logger = logging.getLogger("audit")


class AuditLogger:

    def log_user_login(self, user_id: int):
        audit_logger.info(f"User login: {user_id}")

    def log_order_created(self, order_id: int):
        audit_logger.info(f"Order created: {order_id}")

    def log_stock_movement(self, book_id: int, from_cell: int, to_cell: int, qty: int):
        audit_logger.info(
            f"Stock movement: book={book_id}, from={from_cell}, to={to_cell}, qty={qty}"
        )
